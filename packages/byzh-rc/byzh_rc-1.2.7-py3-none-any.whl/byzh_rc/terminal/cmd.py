import subprocess
def BRunCmd(*args, show=True):
    command = ''
    for i in range(len(args)):
        if i == len(args) - 1:
            command += str(args[i])
            break
        command += str(args[i]) + ' && '
    if show:
        command = f'start cmd /K "{command}"'
    # print(command)
    subprocess.run(command, shell=True)

if __name__ == '__main__':
    BRunCmd("echo hello","echo world","echo awa", show=True)