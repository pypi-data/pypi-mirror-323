import requests
import urllib3
# from proxmox_client.types import HeaderModel, Certificate, ProxyHost


class ProxmoxClient:
    """
    ProxmoxClient class.
    Require:
        - base_url: Proxmox WebUI url
        - login: Proxmox WebUI login
        - password: Proxmox WebUI password
    """

    def __init__(self, base_url, login, password):
        urllib3.disable_warnings()
        self.session = requests.Session()
        self.base_url = base_url
        self.__auth(login, password)

    def __auth(self, login, password):
        """
        Create session
        Require:
            - login: Proxmox username
            - password: Proxmox password
        """
        response = self.session.post(
            f"{self.base_url}/api2/json/access/ticket",
            json={"username": login, "password": password},
            verify=False,
        )
        data = response.json()
        self.ticket = {'PVEAuthCookie': data['data']['ticket']}
        self.CSRF = data['data']['CSRFPreventionToken']

    def connect(self, conn_type, option, post_data):
        """
        The main communication method.
        """
        self.full_url = "%s/api2/json/%s" % (self.base_url,option)

        httpheaders = {'Accept':'application/json'}

        if conn_type == "post":
            httpheaders['CSRFPreventionToken'] = str(self.CSRF)
            self.response = requests.post(
                self.full_url, 
                verify=False, 
                data = post_data, 
                cookies = self.ticket,
                headers = httpheaders
            )

        elif conn_type == "put":
            httpheaders['CSRFPreventionToken'] = str(self.CSRF)
            self.response = requests.put(
                self.full_url, 
                verify=False, 
                data = post_data, 
                cookies = self.ticket,
                headers = httpheaders
            )

        elif conn_type == "delete":
            httpheaders['CSRFPreventionToken'] = str(self.CSRF)
            self.response = requests.delete(
                self.full_url, 
                verify=False, 
                data = post_data, 
                cookies = self.ticket,
                headers = httpheaders
            )
        elif conn_type == "get":
            self.response = requests.get (
                self.full_url, 
                verify=False, 
                cookies = self.ticket
            )

        self.returned_data = self.response.json()
        if self.response.status_code != requests.codes.ok:                   
            if not self.returned_data['data']:
                self.returned_data['data'] = self.response.status_code
        elif not self.returned_data['data']:
            self.returned_data['data'] = 0                   
        return self.returned_data

    # Cluster Methods

    def getClusterStatus(self):
        """Get cluster status information. Returns JSON"""
        data = self.connect('get','cluster/status', None)
        return data
    
    def getClusterBackupSchedule(self):
        """List vzdump backup schedule. Returns JSON"""
        data = self.connect('get','cluster/backup',None)
        return data

    def getClusterVmNextId(self):
        """Get next VM ID of cluster. Returns JSON"""
        data = self.connect('get','cluster/nextid',None)
        return data

    def getPools(self):
        """Get list of pools. Returns JSON"""
        data = self.connect('get','pools',None)
        return data

    def getNodes(self):
        """Get list of nodes. Returns JSON"""
        data = self.connect('get','nodes',None)
        return data
    
    def getNodeNetworks(self,node):
        """List available networks. Returns JSON"""
        data = self.connect('get','nodes/%s/network' % (node),None)
        return data

    def getNodeInterface(self,node,interface):
        """Read network device configuration. Returns JSON"""
        data = self.connect('get','nodes/%s/network/%s' % (node,interface),None)
        return data

    def getNodeContainerIndex(self,node):
        """LXC container index (per node). Returns JSON"""
        data = self.connect('get','nodes/%s/lxc' % (node),None)
        return data

    def getNodeVirtualIndex(self,node):
        """Virtual machine index (per node). Returns JSON"""
        data = self.connect('get','nodes/%s/qemu' % (node),None)
        return data

    def getNodeServiceList(self,node):
        """Service list. Returns JSON"""
        data = self.connect('get','nodes/%s/services' % (node),None)
        return data

    def getNodeServiceState(self,node,service):
        """Read service properties"""
        data = self.connect('get','nodes/%s/services/%s/state' % (node,service),None)
        return data

    def getNodeStorage(self,node):
        """Get status for all datastores. Returns JSON"""
        data = self.connect('get','nodes/%s/storage' % (node),None)
        return data

    def getNodeFinishedTasks(self,node):
        """Read task list for one node (finished tasks). Returns JSON"""
        data = self.connect('get','nodes/%s/tasks' % (node),None)
        return data

    def getNodeDNS(self,node):
        """Read DNS settings. Returns JSON"""
        data = self.connect('get','nodes/%s/dns' % (node),None)
        return data

    def getNodeStatus(self,node):
        """Read node status. Returns JSON"""
        data = self.connect('get','nodes/%s/status' % (node),None)
        return data

    def getNodeSyslog(self,node):
        """Read system log. Returns JSON"""
        data = self.connect('get','nodes/%s/syslog' % (node),None)
        return data

    def getNodeRRD(self,node):
        """Read node RRD statistics. Returns PNG"""
        data = self.connect('get','nodes/%s/rrd' % (node),None)
        return data

    def getNodeRRDData(self,node):
        """Read node RRD statistics. Returns RRD"""
        data = self.connect('get','nodes/%s/rrddata' % (node),None)
        return data

    def getNodeBeans(self,node):
        """Get user_beancounters failcnt for all active containers. Returns JSON"""
        data = self.connect('get','nodes/%s/ubfailcnt' % (node),None)
        return data

    def getNodeTaskByUPID(self,node,upid):
        """Get tasks by UPID. Returns JSON"""
        data = self.connect('get','nodes/%s/tasks/%s' % (node,upid),None)
        return data

    def getNodeTaskLogByUPID(self,node,upid):
        """Read task log. Returns JSON"""
        data = self.connect('get','nodes/%s/tasks/%s/log' % (node,upid),None)
        return data

    def getNodeTaskStatusByUPID(self,node,upid):
        """Read task status. Returns JSON"""
        data = self.connect('get','nodes/%s/tasks/%s/status' % (node,upid),None)
        return data
    
    # LXC Methods

    def getContainers(self,node):
        """Directory index. Returns JSON"""
        data = self.connect('get','nodes/%s/lxc' % node,None)
        return data

    def getContainerIndex(self,node,vmid):
        """Directory index. Returns JSON"""
        data = self.connect('get','nodes/%s/lxc/%s' % (node,vmid),None)
        return data

    def getContainerStatus(self,node,vmid):
        """Get virtual machine status. Returns JSON"""
        data = self.connect('get','nodes/%s/lxc/%s/status/current' % (node,vmid),None)
        return data

    def getContainerBeans(self,node,vmid):
        """Get container user_beancounters. Returns JSON"""
        data = self.connect('get','nodes/%s/lxc/%s/status/ubc' % (node,vmid),None)
        return data

    def getContainerConfig(self,node,vmid):
        """Get container configuration. Returns JSON"""
        data = self.connect('get','nodes/%s/lxc/%s/config' % (node,vmid),None)
        return data

    def getContainerInitLog(self,node,vmid):
        """Read init log. Returns JSON"""
        data = self.connect('get','nodes/%s/lxc/%s/initlog' % (node,vmid),None)
        return data

    def getContainerRRD(self,node,vmid):
        """Read VM RRD statistics. Returns PNG"""
        data = self.connect('get','nodes/%s/lxc/%s/rrd' % (node,vmid),None)
        return data

    def getContainerRRDData(self,node,vmid):
        """Read VM RRD statistics. Returns RRD"""
        data = self.connect('get','nodes/%s/lxc/%s/rrddata' % (node,vmid),None)
        return data

    def getContainerSnapshots(self,node,vmid):
        """Read VM RRD statistics. Returns RRD"""
        data = self.connect('get','nodes/%s/lxc/%s/snapshot' % (node,vmid),None)
        return data
    
    def createLXCContainer(self,node,post_data):
        """
        Create or restore a container. Returns JSON
        Requires a dictionary of tuples formatted [('postname1','data'),('postname2','data')]
        """
        data = self.connect('post','nodes/%s/lxc' % node, post_data)
        return data

    def mountLXCPrivate(self,node,vmid):
        """Mounts container private area. Returns JSON"""
        post_data = None
        data = self.connect('post','nodes/%s/lxc/%s/status/mount' % (node,vmid), post_data)
        return data

    def shutdownLXCContainer(self,node,vmid):
        """Shutdown the container. Returns JSON"""
        post_data = None
        data = self.connect('post','nodes/%s/lxc/%s/status/shutdown' % (node,vmid), post_data)
        return data

    def startLXCContainer(self,node,vmid):
        """Start the container. Returns JSON"""
        post_data = None
        data = self.connect('post','nodes/%s/lxc/%s/status/start' % (node,vmid), post_data)
        return data

    def stopLXCContainer(self,node,vmid):
        """Stop the container. Returns JSON"""
        post_data = None
        data = self.connect('post','nodes/%s/lxc/%s/status/stop' % (node,vmid), post_data)
        return data

    def rebootLXCContainer(self,node,vmid):
        """Reboot the container. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/lxc/%s/status/reboot" % (node,vmid), post_data)
        return data

    def unmountLXCPrivate(self,node,vmid):
        """Unmounts container private area. Returns JSON"""
        post_data = None
        data = self.connect('post','nodes/%s/lxc/%s/status/unmount' % (node,vmid), post_data)
        return data

    def migrateLXCContainer(self,node,vmid,target):
        """Migrate the container to another node. Creates a new migration task. Returns JSON"""
        post_data = {'target': str(target)}
        data = self.connect('post','nodes/%s/lxc/%s/migrate' % (node,vmid), post_data)
        return data

    def snapshotLXCContainer(self,node,vmid,post_data):
        """Snapshot the container, Returns JSON"""
        #post_data = {'target': str(target)}
        data = self.connect('post','nodes/%s/lxc/%s/snapshot' % (node,vmid), post_data)        
        return data

    def rollbackSnapshotLXCContainer(self,node,vmid,snapname):
        """Rollback the snapshotted container, Returns JSON"""
        post_data = {}
        data = self.connect('post','nodes/%s/lxc/%s/snapshot/%s/rollback' % (node,vmid,snapname), post_data)        
        return data

    # KVM Methods

    def getVirtualIndex(self,node,vmid):
        """Directory index. Returns JSON"""
        data = self.connect('get','nodes/%s/qemu/%s' % (node,vmid),None)
        return data

    def getVirtualStatus(self,node,vmid):
        """Get virtual machine status. Returns JSON"""
        data = self.connect('get','nodes/%s/qemu/%s/status/current' % (node,vmid),None)
        return data

    def getVirtualConfig(self,node,vmid):
        """Get virtual machine configuration. Returns JSON"""
        data = self.connect('get','nodes/%s/qemu/%s/config' % (node,vmid),None)
        return data

    def getVirtualRRD(self,node,vmid):
        """Read VM RRD statistics. Returns JSON"""
        data = self.connect('get','nodes/%s/qemu/%s/rrd' % (node,vmid),None)
        return data

    def getVirtualRRDData(self,node,vmid):
        """Read VM RRD statistics. Returns JSON"""
        data = self.connect('get','nodes/%s/qemu/%s/rrddata' % (node,vmid),None)
        return data
    
    def createVirtualMachine(self,node,post_data):
        """
        Create or restore a virtual machine. Returns JSON
        Requires a dictionary of tuples formatted [('postname1','data'),('postname2','data')]
        """
        data = self.connect('post',"nodes/%s/qemu" % (node), post_data)
        return data

    def cloneVirtualMachine(self,node,vmid,post_data):
        """
        Create a copy of virtual machine/template
        Requires a dictionary of tuples formatted [('postname1','data'),('postname2','data')]
        """
        data = self.connect('post',"nodes/%s/qemu/%s/clone" % (node,vmid), post_data)
        return data

    def resetVirtualMachine(self,node,vmid):
        """Reset a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/status/reset" % (node,vmid), post_data)
        return data

    def resumeVirtualMachine(self,node,vmid):
        """Resume a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/status/resume" % (node,vmid), post_data)
        return data

    def shutdownVirtualMachine(self,node,vmid):
        """Shut down a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/status/shutdown" % (node,vmid), post_data)
        return data

    def startVirtualMachine(self,node,vmid):
        """Start a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/status/start" % (node,vmid), post_data)
        return data
    
    def rebootVirtualMachine(self,node,vmid):
        """Reboot a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/status/reboot" % (node,vmid), post_data)
        return data

    def stopVirtualMachine(self,node,vmid):
        """Stop a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/status/stop" % (node,vmid), post_data)
        return data

    def suspendVirtualMachine(self,node,vmid):
        """Suspend a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/status/suspend" % (node,vmid), post_data)
        return data

    def migrateVirtualMachine(self,node,vmid,target,online=False,force=False):
        """Migrate a virtual machine. Returns JSON"""
        post_data = {'target': str(target)}
        if online:
            post_data['online'] = '1'
        if force:
            post_data['force'] = '1'
        data = self.connect('post',"nodes/%s/qemu/%s/migrate" % (node,vmid), post_data)
        return data

    def monitorVirtualMachine(self,node,vmid,command):
        """Send monitor command to a virtual machine. Returns JSON"""
        post_data = {'command': str(command)}
        data = self.connect('post',"nodes/%s/qemu/%s/monitor" % (node,vmid), post_data)
        return data

    def vncproxyVirtualMachine(self,node,vmid):
        """Creates a VNC Proxy for a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/vncproxy" % (node,vmid), post_data)
        return data

    def rollbackVirtualMachine(self,node,vmid,snapname):
        """Rollback a snapshot of a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post',"nodes/%s/qemu/%s/snapshot/%s/rollback" % (node,vmid,snapname), post_data)
        return data

    def getSnapshotConfigVirtualMachine(self,node,vmid,snapname):
        """Get snapshot config of a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('get',"nodes/%s/qemu/%s/snapshot/%s/config" % (node,vmid,snapname), post_data)
        return data