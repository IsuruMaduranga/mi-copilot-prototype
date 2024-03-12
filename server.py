#####################################################################
#  Copyright (c) WSO2 LLC. (http://www.wso2.org) All Rights Reserved.
#
#  WSO2 LLC. licenses this file to you under the Apache License,
#  Version 2.0 (the "License"); you may not use this file except
#  in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#####################################################################

import uvicorn
import io
import yaml
from copilot.api import api

# Auto generate openapi.yaml when the server starts
openapi_json= api.openapi()
yaml_s = io.StringIO()
yaml.dump(openapi_json, yaml_s, allow_unicode=True, sort_keys=False)
with open("openapi.yaml", "w") as f:
    f.write(yaml_s.getvalue())

if __name__ == "__main__":    
    uvicorn.run(api, host="0.0.0.0", port=8000)
