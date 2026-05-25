conditions = {}
machine_name = "Maskin 1"
group_id = 2

if machine_name:
    conditions["machineName"]= machine_name
if group_id:
    conditions["groupID"]= group_id
print(f"********************************************************************************* TYPE: {type(conditions)} VALUE: {group_id} *******************************")
