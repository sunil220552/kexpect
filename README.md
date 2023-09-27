# k8sExpect
Pexpect like-module to interact with Kubernetes based container's shell.



# Installation
```
pip install .
```

# Usage
```
from k8sExpect import k8sExpect
import time

# Create a k8sExpect object
k = k8sExpect()

# Connect to a pod
k.connect("pod-name", "namespace", "container-name")

# Send a command
k.sendline("ls -l")

# Wait for the command to complete
k.expect("user@pod-name:~\$")

# Print the output
print(k.before)

# Send another command
k.sendline("echo 'hello world'")
k.expect("user@pod-name:~\$")

# Print the output
print(k.before)

# Close the connection
k.close()
```

# Example
```
from k8sExpect import k8sExpect
import time

# Create a k8sExpect object
k = k8sExpect()

# Connect to a pod
k.connect("pod-name", "namespace", "container-name")

# Send a command
k.sendline("ls -l")

# Wait for the command to complete
k.expect("user@pod-name:~\$")

# Print the output
print(k.before)

# Send another command
k.sendline("echo 'hello world'")
k.expect("user@pod-name:~\$")

# Print the output
print(k.before)

# Close the connection
k.close()
```

