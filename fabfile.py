from fabric.api import run
from fabric.api import env
import boto
import boto.ec2
import time
from fabric.api import prompt
from fabric.api import execute
from fabric.api import sudo
from fabric.contrib.project import upload_project
from fabric.contrib.project import rsync_project
import os

env.hosts = ['localhost', ]
env.aws_region = 'us-west-2'


def host_type():
    run('uname -s')


def get_ec2_connection():
    if 'ec2' not in env:
        conn = boto.ec2.connect_to_region(env.aws_region)
        if conn is not None:
            env.ec2 = conn
            print "Connected to EC2 region %s" % env.aws_region
        else:
            msg = "Unable to connect to EC2 region %s"
            raise IOError(msg % env.aws_region)
    return env.ec2


def provision_instance(wait_for_running=False, timeout=60, interval=2):
    wait_val = int(interval)
    timeout_val = int(timeout)
    conn = get_ec2_connection()
    instance_type = 't1.micro'
    key_name = 'robertskey'
    security_group = 'ssh-access'
    image_id = 'ami-810a2fb1'

    reservations = conn.run_instances(
        image_id,
        key_name=key_name,
        instance_type=instance_type,
        security_groups=[security_group, ]
    )
    new_instances = [i for i in reservations.instances if i.state == u'pending']
    running_instance = []
    if wait_for_running:
        waited = 0
        while new_instances and (waited < timeout_val):
            time.sleep(wait_val)
            waited += int(wait_val)
            for instance in new_instances:
                state = instance.state
                print "Instance %s is %s" % (instance.id, state)
                if state == "running":
                    running_instance.append(
                        new_instances.pop(new_instances.index(i))
                    )
                    running_instance = running_instance
                instance.update()


def stop_running_instances():
    list_aws_instances(state='running')
    running_instances = env.instances
    instance_ids = []
    for instance in running_instances:
        instance_ids.append(instance['id'])
    conn = get_ec2_connection()
    conn.stop_instances(instance_ids)


def terminate_stopped_instances():
    list_aws_instances(state='stopped')
    stopped_instances = env.instances
    instance_ids = []
    for instance in stopped_instances:
        instance_ids.append(instance['id'])
    conn = get_ec2_connection()
    conn.terminate_instances(instance_ids)


def list_aws_instances(verbose=False, state='all'):
    conn = get_ec2_connection()

    reservations = conn.get_all_reservations()
    instances = []
    for res in reservations:
        for instance in res.instances:
            if state == 'all' or instance.state == state:
                instance = {
                    'id': instance.id,
                    'type': instance.instance_type,
                    'image': instance.image_id,
                    'state': instance.state,
                    'instance': instance,
                }
                instances.append(instance)
    env.instances = instances
    if verbose:
        import pprint
        pprint.pprint(env.instances)


def select_instance(state='running'):
    if env.get('active_instance', False):
        return

    list_aws_instances(state=state)

    prompt_text = "Please select from the following instances:\n"
    instance_template = " %(ct)d: %(state)s instance %(id)s\n"
    for idx, instance in enumerate(env.instances):
        ct = idx + 1
        args = {'ct': ct}
        args.update(instance)
        prompt_text += instance_template % args
    prompt_text += "Choose an instance: "

    def validation(input):
        choice = int(input)
        if not choice in range(1, len(env.instances) + 1):
            raise ValueError("%d is not a valid instance" % choice)
        return choice

    choice = prompt(prompt_text, validate=validation)
    env.active_instance = env.instances[choice - 1]['instance']


def run_command_on_selected_server(command):
    select_instance()
    selected_hosts = [
        'ubuntu@' + env.active_instance.public_dns_name
    ]
    execute(command, hosts=selected_hosts)


def _install_nginx():
    sudo('apt-get install nginx')
    sudo('/etc/init.d/nginx start')


def install_nginx():
    run_command_on_selected_server(_install_nginx)


def _apt_get_install():
    sudo('apt-get install supervisor')


def _restart_nginx():
    sudo('/etc/init.d/nginx restart')


def _run_supervisor():
    sudo('supervisord -c supervisord.conf')


def _unlink_supervisor():
    sudo('sudo unlink /tmp/supervisor.sock')


def deploy():
    os.system('rsync -r  newstuff/* ubuntu@ec2-52-10-176-172.us-west-2.compute.amazonaws.com:~/')
    run_command_on_selected_server(_restart_nginx)
    run_command_on_selected_server(_unlink_supervisor)
    run_command_on_selected_server(_run_supervisor)
