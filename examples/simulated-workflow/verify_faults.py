import sys, importlib.util, json
from pathlib import Path
d=Path(__file__).resolve().parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
fixture=load('sim_fixture',d/'conftest.py');query=load('sim_query',d/'test_get_mode.py');setter=load('sim_setter',d/'test_set_mode.py')
checks=[]
class WrongQuery(fixture.MemoryConfig):
 def get_mode(self):return 'unexpected'
try:query.test_get_mode(WrongQuery(),{'expected':'idle'})
except AssertionError:checks.append('query rejects wrong business value')
else:raise AssertionError('query accepted wrong value')
class WrongReturn(fixture.MemoryConfig):
 def set_mode(self,mode):
  result=super().set_mode(mode)
  return {'accepted':False} if mode=='eco' else result
obj=WrongReturn()
try:setter.test_set_mode(obj,{'mode':'eco','expected_return':{'accepted':True}})
except AssertionError:pass
else:raise AssertionError('setter accepted wrong business response')
assert obj.mode=='idle' and obj.calls[-1]==('get_mode',);checks.append('failed setter assertion still restores and reads original')
class RestoreFailure(fixture.MemoryConfig):
 def set_mode(self,mode):
  if mode=='idle':raise RuntimeError('simulated restore failure')
  return super().set_mode(mode)
obj=RestoreFailure()
try:setter.test_set_mode(obj,{'mode':'eco','expected_return':{'accepted':True}})
except RuntimeError:checks.append('restore failure is observable')
else:raise AssertionError('restore failure hidden')
class BothFailure(RestoreFailure):
 def set_mode(self,mode):
  result=super().set_mode(mode)
  return {'accepted':False} if mode=='eco' else result
try:setter.test_set_mode(BothFailure(),{'mode':'eco','expected_return':{'accepted':True}})
except AssertionError as e:
 assert isinstance(e.__cause__,RuntimeError);checks.append('business failure retains restoration failure as cause')
else:raise AssertionError('original failure lost')
obj=fixture.MemoryConfig();setter.test_set_mode_invalid(obj,{'mode':'invalid'});assert obj.mode=='idle';checks.append('specific exception leaves original state unchanged')

service_query=load('sim_service_query',d/'test_service_get_mode.py')
service_setter=load('sim_service_setter',d/'test_service_set_mode.py')
class WrongServiceQuery(fixture.MemoryService):
 def call(self,service,request,timeout_s):return {'success':True,'data':'wrong'}
try:service_query.test_service_get_mode(WrongServiceQuery(),{'expected':'idle','timeout_s':0.5})
except AssertionError:checks.append('service success alone does not pass wrong business value')
else:raise AssertionError('service accepted wrong business value')
obj=fixture.MemoryService()
try:service_setter.test_service_set_mode(obj,{'parameters':{'mode':'eco'},'expected_return':'wrong','expected_data':'eco','timeout_s':0.5})
except AssertionError:pass
else:raise AssertionError('service accepted wrong return')
assert obj.mode=='idle' and obj.requests[-1][0]=='get_mode'
assert all(set(request)<= {'mode'} for _,request,_ in obj.requests)
checks.append('service failure restores state and excludes validation controls from requests')
print(json.dumps({'passed':True,'checks':checks,'scope':'fictional memory SDK and Service only'},ensure_ascii=False,indent=2))
