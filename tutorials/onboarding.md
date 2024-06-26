# Course Onboarding

## TL;DR

Onboarding steps:

- [Git](#git) and [GitHub account](#GitHub)
- [Ubuntu Desktop workstation](#linux-operating-system)
- [PyCharm (or any other alternative)](#pycharm)
- [Clone the course repo](#clone-the-course-repository-into-pycharm)

## GitHub

The website you are visiting now is called **GitHub**.
It's a platform where millions of developers from all around the world collaborate on projects and share code. 

Each project on GitHub is stored in something called a **Git repository**, or **repo** for short. 
A Git repository is like a folder that contains all the files and resources related to a project.
These files can include code, images, documentation, and more.

The content of this course, including all code files, tutorials, and project, are also stored and provided to you as a Git repo.

Create [GitHub account](https://github.com/) if you haven't already.

## Linux Operating System

Throughout the course you'll use the Linux Operating System (**OS**). No Windows here...

There exist many different [distributions of Linux](https://en.wikipedia.org/wiki/Linux_distribution). 
We will use **Ubuntu**, which is a user-friendly Linux distribution known for its stability, security, and vast community support. 

The course content was written and tested with **Ubuntu 20.04** or **22.04**, 
we recommend using either of these versions for the best experience.

Below you'll find various ways to install Ubuntu.

### Virtualized Ubuntu using VirtualBox

A common way to set up Ubuntu is to install it on a virtual machine (VM), on top of your existed Windows installation.

There are many different virtualization platforms such as VMWere or VirtualBox. 

VirtualBox offers a free virtual machine license for personal, educational, or evaluation use.

VM requirements:

- At least 8GB of RAM.
- At least 80GB disk space.

Follow the below tutorial:   
https://ubuntu.com/tutorials/how-to-run-ubuntu-desktop-on-a-virtual-machine-using-virtualbox

In addition, enable clipboard sharing between your Windows and the Ubuntu VM:   
https://linuxhint.com/enable-copy-paste-virtualbox-host/


### Native Ubuntu

Another recommended way is to install Ubuntu Desktop directly on your machine, without a virtualization layer. 
You can have Ubuntu as your primary OS, or choose to install it next to an existing Windows installation. 

To install Ubuntu as your primary OS:    
https://ubuntu.com/tutorials/install-ubuntu-desktop


To install Ubuntu along with your existed Windows:   
https://www.freecodecamp.org/news/how-to-dual-boot-windows-10-and-ubuntu-linux-dual-booting-tutorial/

## Git

**Git** is a version control system (**VCS**), it allows a team to collaborate on the same code project, and save different versions of the code without interfering each other.  
Git is the most popular VCS, you'll find it in almost every software project. 

On your Ubuntu, install Git form: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

As for the difference between **Git** and **GitHub**:   
Git is the tool used for managing the source code on your local machine, while GitHub is a platform that hosts Git projects (a **Hub**).

## PyCharm

PyCharm is an Integrated Development Environment (**IDE**) software for code development, with Python as the primary programming language. 

The course's content was written with PyCharm as the preferred IDE. 

You can use any other IDE of your choice (e.g. VSCode), but keep in mind that you may experience some differences in functionality and workflow compared to PyCharm.
Furthermore, when it comes to Python programming, PyCharm reigns supreme - unless you enjoy arguing with your tools! 

> [!NOTE]
> The last sentence was generated by ChatGPT. For me there is nothing funny in PyCharm vs VSCode debate.

On your Ubuntu, install PyCharm community from: https://www.jetbrains.com/pycharm/download/#section=linux (scroll down for community version).

### Clone the course repository into PyCharm

Cloning a GitHub project creates a local copy of the repository on your local computer.

[Read here](https://www.jetbrains.com/help/pycharm/set-up-a-git-repository.html#clone-repo) how to clone our GitHub repository into your PyCharm environment.
When you have to specify the repo URL, enter:

```text
https://github.com/alonitac/DevOpsTheHardWay
```

At the end, you should have an opened PyCharm project with all the files and folders from the cloned GitHub repository, ready for you to work with.

