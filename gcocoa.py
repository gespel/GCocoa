'''logging:
  receivers:
    TestApp:
      type: files
      include_paths:
        - /var/log/testapp.log

  processors:
    modify_severity:
      type: modify_fields
      fields:
        severity:
          copy_from: jsonPayload.level
          map_values:
            "info": "INFO"
            "warning": "WARN"

    testapp_json:
      type: parse_json

  service:
    pipelines:
      default_pipeline:
        receivers: [TestApp]
        processors: [testapp_json, modify_severity]
'''
import yaml

class Receiver:
    def __init__(self, name, type, include_paths):
        self.name = name
        self.type = type
        self.include_paths = include_paths
        self.d = {
            f"{self.name}": {
                "type": self.type,
                "include_paths": self.include_paths
            }
        }
    
    def get_name(self):
        return self.name
    
    def get_body(self):
        return self.d[self.name]
    
class Processor:
    def __init__(self, name, type, dst_field_name, src_field_name, mappings):
        self.name = name
        self.type = type
        self.dst_field_name = dst_field_name
        self.src_field_name = src_field_name
        self.mappings = mappings
        self.d = {
            f"{self.name}": {
                "type": self.type,
                "fields": {
                    f"{self.dst_field_name}": {
                        "copy_from": self.src_field_name,
                        "map_values": self.mappings
                    }
                }
            }
        }

    def get_name(self):
        return self.name
    
    def get_body(self):
        return self.d[self.name]

class Service:
    def __init__(self, name, sub_name, receivers, processors):
        self.name = name
        self.sub_name = sub_name
        self.receivers = receivers
        self.processors = processors
        self.d = {
            f"{self.name}": {
                f"{self.sub_name}": {
                    "receivers": self.receivers,
                    "processors": self.processors
                }
            }
        }
    
    def get_name(self):
        return self.name

    def get_body(self):
        return self.d[self.name]

def assemble_ops_agent_config(receivers, processors, services):
    out = {
        "logging": {
            "receivers": {},
            "processors": {},
            "service": {}
        }
    }
    for receiver in receivers:
        out["logging"]["receivers"][receiver.get_name()] = receiver.get_body()

    for processor in processors:
        out["logging"]["processors"][processor.get_name()] = processor.get_body()

    for service in services:
        out["logging"]["service"][service.get_name()] = service.get_body()

    return yaml.dump(out)


r = Receiver("TestApp", "files", ["/var/log/testapp.log"])
p = Processor("modify_severity", "modify_fields", "severity", "jsonPayload.level", {"info": "INFO", "warning": "WARN"})
s = Service("pipelines", "default_pipeline", ["TestApp"], ["modify_severity"])

print(assemble_ops_agent_config([r], [p], [s]))