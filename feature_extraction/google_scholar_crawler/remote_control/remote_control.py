import paramiko


class RemoteControl:
    def __init__(self, host):
        self.host = host
        self.user = 'root'
        self.password = 'meng0124xiang'
        self.__ssh_fd = self.ssh_connect()

    def ssh_connect(self):
        try:
            sfd = paramiko.SSHClient()
            sfd.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sfd.connect(self.host, username=self.user, password=self.password)
        except Exception as e:
            print('ssh %s@%s: %s' % (self.user, self.host, e))
            raise()
        return sfd

    def ssh_exec(self, command):
        return self.__ssh_fd.exec_command(command)

    def scp(self, from_path, to_path):
        sftp = self.__ssh_fd.open_sftp()
        sftp.put(from_path, to_path)
        sftp.close()

    def close(self):
        self.__ssh_fd.close()


if __name__ == '__main__':
    rc = RemoteControl('45.79.20.192')
    stdin, stdout, stderr = rc.ssh_exec('apt-get -y install python3-pip; pip3 install simplejson; pip3 install bs4')
    err_list = stderr.readlines()

    if len(err_list) > 0:
        print('ERROR:' + err_list[0])
        exit()

    for item in stdout.readlines():
        print(item)



