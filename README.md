# CS244 '17 PA3: Mahimahi
## Reproducing our reproductions
Here we provide instructions for running the experiment sequentially. Since our measurements take a long time to run, we provide a shorter version with eight websites, running each measurement only five times.

*We apologize in advance for the complicated instructions. The complications mostly arise from our reliance on specific Linux kernel features (see the “Challenges” section); this is why we’re providing an image for you to use.*

1. Create a Google Storage bucket in your project [like this](https://cloud.google.com/storage/docs/creating-buckets). (You can choose the **Multi-Regional** storage class and **United States** as the location.)
2. Download our image [here](https://storage.googleapis.com/mahimahi/cs244_pa3_mahimahi.tar.gz). If it doesn't work, here's another [link](https://www.dropbox.com/s/vk30gcqur11ps7f/cs244_pa3_mahimahi.tar.gz?dl=0).
3. Upload our image to your bucket [like this](https://cloud.google.com/storage/docs/cloud-console#_uploadingdata). You should now see our image listed in the bucket.
4. Go to the [Images](https://console.cloud.google.com/compute/images) page and click on **Create Image**. Give it a name, choose **Cloud Storage File** for **Source**, click on **Browse**, and locate the image you just uploaded to your bucket. Click on **Create**.
5. Launch a VM from the [VM Instances](https://console.cloud.google.com/compute/instances) page (click on **Create Instance**) with these parameters:
  - Zone: **us-east1-c**
  - Machine type: **2 vCPUs** (should say 7.5 GB memory by default)
  - Boot disk: click on **Change**, go to the **Custom images** tab, and choose the image you imported in Step 4; use 20 GB of Standard persistent disk
  - Firewall: **Allow HTTP traffic**
  - Click on **Management, disk, networking, SSH keys**. Under **Metadata**, enter:
    - Key: `serial-port-enable`
    - Value: `1`
  - Click on **Create** and wait for the instance to be launched.
6. When the instance has been successfully launched, click on the instance name, scroll to the bottom, and click on **Connect to serial port**.
7. When the console window has loaded, enter `fsck /dev/sda1 -f`. When asked whether to fix errors, always press **y**. When `fsck` is done, close the console window.
8. Click on **Reset** and wait for a minute or two.
9. Find the **External IP** on the same page, and ssh into it (user: **cs244**, password: **cs244**)
  - You can type `ssh cs244@xxx.xxx.xxx.xxx` in the terminal and enter the password.
  - Alternatively, go back to the [VM Instances](https://console.cloud.google.com/compute/instances) page and click on **SSH** next to this instance. After you’re logged in, type `su cs244`, enter the password, and type `cd` to go back to the home directory.
10. Type `cd cs244-pa3-mahimahi`.
11. You’re now ready to run the experiment! The short version may take up to 1.5 hours. To run the experiment in the background, type `screen` and press <Enter>, then type `./reproduce.sh`. You should see something like:
    ```
    DELAY = 100, TRACE = 5Mbps_trace, RUNS = 5
    
    Sun Jun  4 21:54:11 UTC 2017
    Measuring www.ask.com
    Mahimahi raw...
    0
    ```
12. You can now press Ctrl-A then Ctrl-D to quit `screen`. Feel free to terminate the SSH connection and come back later.
13. When you come back, resume screen by entering `screen -r`. If the experiment has finished, you should see a URL for the graph. Go to that URL in your browser. You should hopefully see a similar but coarser-grained graph, something like this (if it looks very different from our main graph above, it might be because the number of trials/websites was too small):

![Sample output plot](https://d2mxuefqeaa7sj.cloudfront.net/s_6BFA2CF32BCD0EC2AAE8F9BFE9054ABD9D4B6D049A5F91F3301CA6C5163CD742_1496611295640_errs_cdf.png)

