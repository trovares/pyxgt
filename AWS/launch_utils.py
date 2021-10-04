# -*- coding: utf-8 -*- --------------------------------------------------===#
#
#  Copyright 2021 Trovares Inc.
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

import boto3, json, time
import xgt

class LaunchxGT(object):
    def __init__(self, cf_json_file='cfxgt.json', userid='xgtd'):
        self.__userid = userid
        self.__cf_client = boto3.client('cloudformation')
        self.__read_cloudformation(cf_json_file)
        try:
            import ipywidgets as widgets
            from IPython.display import Javascript, display
            self.__widgets_supported = True
        except:
            self.__widgets_supported = False
        self.stack_name = None
        self.__xgt_server = None

    def __read_cloudformation(self, cf_json_file):
        self.cloudformation = None
        with open(cf_json_file, 'r') as cf_file:
            self.__cf_string = cf_file.read()
            self.cloudformation = json.loads(self.__cf_string)
            self.__allowed_instance_types = self.cloudformation['Parameters']['InstanceType']['AllowedValues']

    def request_configuration(self):
        if self.__widgets_supported:
            self.__request_config_using_widgets()
        else:
            self.__request_config_using_input()

    def __request_config_using_input(self):
        self.stack_name = input("Enter stack name: ")
        instance_type = None
        while instance_type not in self.__allowed_instance_types:
            if instance_type is not None:
                print(f"{instance_type} is an unsupported instance type, try again.")
            instance_type = input("Instance Type: ")
        key_name = input("Key Name (e.g., name of *.pem file): ")
        self.parameters = {'KeyName':key_name, 'InstanceType':instance_type}

    def __request_config_using_widgets(self):
        import ipywidgets as widgets
        from IPython.display import Javascript, display

        self.__stack_name_text = widgets.Text()
        stack_name_box = widgets.HBox([widgets.Label('Stack Name:'),
                                       self.__stack_name_text])
        self.__instance_type_dropdown = widgets.Dropdown(
            options=self.__allowed_instance_types,
            layout={'width': 'max-content'},
            value=self.__allowed_instance_types[0],
            disabled=False)
        instance_type_box = widgets.HBox([widgets.Label('Instance Type:'),
                                          self.__instance_type_dropdown])
        self.__key_name_text = widgets.Text()
        key_name_box = widgets.HBox([widgets.Label('Key Name (e.g., name of *.pem file):'),
                                     self.__key_name_text])
        button = widgets.Button(description="Submit")
        form = widgets.VBox([stack_name_box, instance_type_box, key_name_box, button])
        display(form)
        def submit(b):
            # move cursor to next notebook cell
            jscode = "var i = IPython.notebook.get_selected_index(); IPython.notebook.select(i+1);"
            display(Javascript(jscode))
            return None
        button.on_click(submit, False)
        self.parameters = dict()

    def capture_configuration(self):
        if not self.__widgets_supported:
            return
        # Pull data out of input boxes
        self.stack_name = self.__stack_name_text.value
        instance_type = self.__instance_type_dropdown.value
        key_name = self.__key_name_text.value
        self.parameters = {'KeyName':key_name, 'InstanceType':instance_type}

    def stack_is_running(self) -> bool:
        return (self.__prepare_for_stack_operation() and
                self.stack_name in self.stack_map)

    def launch(self):
        if not self.__prepare_for_stack_operation():
            return
        params = [{'ParameterKey':k, 'ParameterValue':v}
                        for (k,v) in self.parameters.items()]
        self.__cf_client.create_stack(
            StackName=self.stack_name,
            TemplateBody=self.__cf_string,
            Parameters=params,
        )
        print("Stack creation initiated", end=" ", flush=True)
        while (self.stack_name not in self.stack_map or
               self.stack_map[self.stack_name]['StackStatus'] == 'CREATE_IN_PROGRESS'):
            time.sleep(1)
            print(".", end="", flush=True)
            self.__prepare_for_stack_operation()
        print("")
        print("Stack creation complete")
        ip = self.get_stack_ip_address()
        print(f"IP Address: {ip}")

    def get_stack_ip_address(self):
        if (not self.__prepare_for_stack_operation() or
                self.stack_name not in self.stack_map):
            return ""
        stack = self.stack_map[self.stack_name]
        outputs = stack['Outputs']
        for output in outputs:
            if output['OutputKey'] == 'PublicIP':
                return output['OutputValue']
        return ""

    def delete_server_stack(self):
        if not self.__prepare_for_stack_operation():
            return
        self.__cf_client.delete_stack(StackName=self.stack_name)
        print("Stack deletion initiated", end=" ", flush=True)
        ip = self.get_stack_ip_address()
        while ip != "":
            time.sleep(1)
            print(".", end="", flush=True)
            ip = self.get_stack_ip_address()
        print("")
        print("Stack deletion complete")
        self.__xgt_server = None

    def __prepare_for_stack_operation(self):
        if self.stack_name is None:
            print("Stack name has not yet been established")
            return False
        stacks = self.__cf_client.describe_stacks()['Stacks']
        self.stack_map = {_['StackName'] : _ for _ in stacks}
        return True

    def xgt_server(self):
        if self.__xgt_server is not None:
            return self.__xgt_server
        ip = self.get_stack_ip_address()
        first_try = True
        while True:
            try:
                self.__xgt_server = xgt.Connection(host=ip,
                                                   userid=self.__userid)
                if not first_try:
                    print("")
                return self.__xgt_server
            except:
                if first_try:
                    print("Waiting for Trovares xGT server to initialize",
                            end=" ", flush=True)
                first_try = False
                time.sleep(1)
                print(".", end="", flush=True)

    def get_xgt_connection_command(self):
        return f"xgt.Connection(host='{self.get_stack_ip_address()}', userid='{self.__userid}')"
