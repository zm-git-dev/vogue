### Prepare Docker container

`docker pull clinicalgenomics/vogue:master-jupyter`

### Create an ssh tunnel to mongoDB on hasta

`ssh -fN -i ~/.ssh/ssh_key -L 27032:localhost:27032 john.doe@hasta.scilifelab.se -o ServerAliveInterval=30`

### Run Docker 

`docker run --rm -t -i -p 27032:27032 -p 8888:8888 -v $(pwd):/home/jovyan clinicalgenomics/vogue:master-jupyter`
