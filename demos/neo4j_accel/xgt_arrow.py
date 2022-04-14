# -*- coding: utf-8 -*- --------------------------------------------------===#
#
#  Copyright 2022 Trovares Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#===----------------------------------------------------------------------===#

import getpass
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.flight as pf
import re
import time
import xgt

def pyarrow_type_to_xgt_type(pyarrow_type):
    if pa.types.is_integer(pyarrow_type):
        return xgt.INT
    if pa.types.is_floating(pyarrow_type):
        return xgt.FLOAT
    if pa.types.is_boolean(pyarrow_type):
        return xgt.BOOLEAN 
    return xgt.TEXT

class BasicClientAuthHandler(pf.ClientAuthHandler):
    def __init__(self, username, password):
        super().__init__()
        self.basic_auth = pf.BasicAuth(username, password)
        self.token = None
    def __init__(self):
        super().__init__()
        self.basic_auth = pf.BasicAuth()
        self.token = None
    def authenticate(self, outgoing, incoming):
        auth = self.basic_auth.serialize()
        outgoing.write(auth)
        self.token = incoming.read()
    def get_token(self):
        return self.token

class GraphSession(xgt.Connection):
    def __init__(self, host="localhost", port=4367, flags=None, userid=None,
                    credentials="", restore_session=False):
        self._user = getpass.getuser() if userid is None else userid
        self._user = self.__validate_userid(self._user)
        #print(f"Userid: {self._user}")
        super().__init__(host=host, port=port, flags=flags, userid=self._user,
                            credentials=credentials)
        self._host = host
        self._port = port
        self._flags = flags
        self._credentials = credentials
        self._default_namespace = self._user.replace('-', "")
        self._answer_table = "_answer_table_"
        self._vertex_frame = dict()
        self._edge_frame = dict()
        #self._server = None
        #self._server = xgt.Connection(host=host, port=port, userid=self._user)
        if not restore_session:
            # zap entire namespace prior to recreating it
            self.drop_namespace(self._user, force_drop = True)
        self.set_default_namespace(self._user)
        self._sandbox_path = None
        c = self.get_config({'system.io_directory'})
        if 'system.io_directory' in c:
            self._sandbox_path = c['system.io_directory']

    def __del__(self):
        self.drop_namespace(self._user, force_drop = True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __str__(self):
        res = ""
        vertex_frames = self.get_vertex_frames(namespace=self._default_namespace)
        for v in vertex_frames:
            res += f"Vertex frame {v.name} contains {v.num_rows:,} vertices.\n"
        edge_frames = self.get_edge_frames(namespace=self._default_namespace)
        for e in edge_frames:
            res += f"Edge frame {e.name} contains {e.num_rows:,} edges.\n"
        return res

    def vertex(self, name, data, key):
        schema = self.__data_schema(data)
        v = self.__create_vertex_frame_from_pyarrow(name, schema, key)
        self.__upload_data(data, v)
        return self

    def edge(self, name, data, direction, source_key, target_key):
        schema = self.__data_schema(data)
        e = self.__create_edge_frame(name, schema, direction, source_key, target_key)
        t0 = time.time()
        self.__upload_data(data, e)
        #print(f"Time to upload: {time.time() - t0:,.2f}")
        return self

    def arrow_edge_writer(self, frame_name, schema, direction, source_key, target_key):
        self.__create_edge_frame(frame_name, schema, direction, source_key, target_key)
        arrow_conn = pf.FlightClient((self._host, self._port))
        arrow_conn.authenticate(BasicClientAuthHandler())
        writer, _ = arrow_conn.do_put(
            pf.FlightDescriptor.for_path(self._default_namespace, frame_name),
            schema)
        return writer

    def query(self, query, params={}, wait=True):
        m = re.search(r'(?<=INTO)\s\w+', query)
        if m is None:
            query = query + f"\nINTO {self._answer_table}"
        self.drop_frame(self._answer_table)
        if wait:
            j = self.run_job(query, parameters=params)
        else:
            j = self.schedule_job(query, parameters=params)
        return j.id

    def get_answers(self, table_name=None):
        name = self._answer_table if table_name is None else table_name
        answers = self.get_table_frame(name)
        return answers.get_data()

    def get_answers_as_pandas(self, table_name=None):
        name = self._answer_table if table_name is None else table_name
        answers = self.get_table_frame(name)
        return answers.get_data_pandas()

    def wait_for_query(self, jobid):
        self.wait_for_job(jobid)

    def __validate_userid(self, userid):
        return userid.replace('.', '_').replace(' ', '_')

    def __data_schema(self, data):
        """
        Determine the schema of data.  Current source categories are:
          * Python arrow Table
          * Pandas DataFrame
          * string holding name of a file:
            - may be an absolute path or a relative path
        
        The return is a pyarrow schema.
        """
        if isinstance(data, pa.Table):
            return data.schema
        if isinstance(data, pd.DataFrame):
            return pq.Table(data).schema
        abspath = os.path.abspath(str(data))
        if os.path.exists(abspath):
            filepath = abspath
            #print(f"Abspath {abspath}")
            #print(f"Sandbox Path: {self._sandbox_path}")
            pfile = pq.ParquetFile(filepath)
            return pfile.schema_arrow
        return None

    def __upload_data(self, data, frame):
        if isinstance(data, pa.Table):
            frame.insert(data.to_pandas())
            return
        if isinstance(data, pd.DataFrame):
            frame.insert(data)
            return
        #print(f"Data path: {data}, sandbox path: {self._sandbox_path}")
        # Try to load directly into server
        try:
            frame.load(f"xgtd://{data}")
            return
        except:
            pass
        # Otherwise, load into client and pass it along
        table = pq.read_table(data)
        path='pq' # 'pandas'
        if path=='pandas':
            frame.insert(table.to_pandas())
            return
        writer = self.arrow_writer(frame_name, table.schema)
        writer.write_table(table)
        writer.close()

    def __create_vertex_frame_from_pyarrow(self, vertex_frame_name, schema, key_column):
        """
        Create a vertex frame using the schema from a pyarrow schema.
        """
        xgt_schema = [(c.name, pyarrow_type_to_xgt_type(c.type)) for c in schema]
        v = self.__create_vertex_frame(vertex_frame_name, xgt_schema, key_column)
        return v
    
    def __create_vertex_frame(self, vertex_frame_name, xgt_schema, key):
        self.drop_frame(vertex_frame_name)
        v = self.create_vertex_frame(name = vertex_frame_name,
                                             schema = xgt_schema, key = key)
        self._vertex_frame[vertex_frame_name] = v
        return v

    def __create_edge_frame(self, edge_frame_name, schema, direction, source_key, target_key):
        """
        Create an edge frame using the schema from a pyarrow schema.

        The direction is a tuple indicating vertex frame names: (source, target)
        """
        xgt_schema = [(c.name, pyarrow_type_to_xgt_type(c.type)) for c in schema]
        xgt_schema_dict = {c[0]: c[1] for c in xgt_schema}
        src, tgt = self.__extract_direction(direction,
                                            xgt_schema_dict[source_key],
                                            xgt_schema_dict[target_key])
        self.drop_frame(edge_frame_name)
        e = self.create_edge_frame(name = edge_frame_name,
                                           schema = xgt_schema,
                                           source = src, source_key = source_key,
                                           target = tgt, target_key = target_key)
        return e

    def __extract_direction(self, direction, default_src_type, default_tgt_type):
        """
        Pulls the names of the source and target nodes from the direction tuple.
        
        Then lookup the source vertex frame.  If it does not exist, create one with a
        single id of a type that matches the source_key in the edge.

        Do the same for the target vertex frame.

        Return a tuple of the (source_frame, target_frame)
        """
        source, target = direction
        try:
            if source in self._vertex_frame:
                src = self._vertex_frame[source]
            else:
                src = self.get_vertex_frame(source)
        except xgt.XgtNameError:
            src = self.__create_vertex_frame(source,
                    [('id', default_src_type)], key = 'id')
        try:
            if target in self._vertex_frame:
                tgt = self._vertex_frame[target]
            else:
                tgt = self.get_vertex_frame(target)
        except xgt.XgtNameError:
            tgt = self.create_vertex_frame(target,
                    [('id', default_tgt_type)], key = 'id')    
        #print(f"Source: {source}, target: {target}")
        return (src, tgt)
