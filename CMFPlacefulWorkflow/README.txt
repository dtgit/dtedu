* Use Site Setup -> Add-on Products panel to install

* Now you can define and apply local workflow policies through the Plone
  Interface.

Overview

  Placeful Workflow is a Plone product that allows you to define workflow
  policies that define content type to workflow mappings that can be applied
  in any sub-folder of your Plone site:

  1. When you access the root of your site, you will see a new action in
     the workflow state drop-down menu called "policy". Click on the 
     "policy" link. 

  2. The next page will let you add a policy to your folder by clicking
     on the "Add Workflow policy" link. Click on "Add Workflow policy".

  3. Now you have a workflow policy in your site, and you can set the
     workflow policies for this folder and below.

  We didn't add any workflow policies, so you don't have a choice
  of different workflow policies yet, so the default workflow
  policy will be taken both for the folder and below.

  Now, let's define a new workflow policy:
  
  1. Access "Site Setup" and click on "Placeful Workflow" in the "Add-on
     Product Configuration" section.

  2. Enter the name "my_policy" in the "New policy" field, and click on
     "add".

  3. Now you have a new policy. Enter the title "Example policy" and the
     description "This is an example policy". 
  
  4. Change the workflow for the content type "Folder" from "folder_workflow"
     to plone_workflow", and click on "Save". Now all your content types
     should use the "plone_workflow".

  Let's test the new workflow policy for "Folders" at the root
  of our site:
  
  1. At the root of the site, select the "Policy" link in the
     workflow state drop-down menu.

  2. Select "Example policy" for "In this Folder" and "Below this Folder" and
     click "Save". 

  3. Then, let's add a Folder to see whether the new workflow policy is 
     active. Go to the root of your site and select "Folder" from 
     the "Add new item" drop-down list. Enter the id "myfolder", the title
     "My folder" and the description "This is my folder", and click on
     "Save". 

  4. Now, when you access the "State" drop-down list, you will see that
     you have the possibility to "submit" the folder. The submit transition
     only exists in the "plone_workflow", and is absent from the 
     "folder_workflow", which demonstrates that the workflow policy we have
     chosen is used for the "Folder" content type.

  Let's go one step further and add a new folder inside of "My folder".
  After having added the new folder, you should also find the "Submit"
  transition available.

  Now it would be interesting to change the workflow policy setting in
  the Plone site. Let's first change the workflow policy for "Below this
  Folder" to "Default Policy". You will find that the second folder does
  not more have the "submit" transition.

  You can add an additional workflow policy in the first folder, which
  assigns the "My policy" for "In this Folder", so the second folder
  will once again have the "submit" transition.

Additional tools

  The Placeful Workflow tool (portal_placeful_workflow) is installed by
  the installer. It provides a few configuration options so that you use
  to create you workflow policies through the ZMI.
