# Description: This script deploys the application to Azure
Param (
    [string] $resourceGroupName ,
    [string] $location ,
    [string] $dockerImageName ,
    [string] $sim_cert_path ,
    [string] $sim_key_path ,
    [string] $csv_path ,
    [string] $docker_registry_pass,
    [string] $docker_registry_server_url,
    [string] $docker_registry_username
)

Write-Host 'This scripts assumes that you have already logged in to Azure using the Azure CLI.'
Write-Host 'If you have not done so, please run the following command:'
Write-Host 'az login'

Write-Host 'This script also assumes you have already created a container registry in Azure and pushed to it'

# prompt for a tenant id
$tenantId = Read-Host -Prompt 'Please enter your tenant id'

# prompt for a subscription id
$subscriptionId = Read-Host -Prompt 'Please enter your subscription id'

# login to azure using tenant id

az login --tenant $tenantId

# set the subscription id
az account set --subscription $subscriptionId

# create resource group
az group create -n $resourceGroupName --location $location

# create deployment group from main template
az deployment group create --resource-group $resourceGroupName --template-file ./main.bicep --parameters docker_image=$dockerImageName location=$location sim_cert_path=$sim_cert_path sim_key_path=$sim_key_path csv_path=$csv_path dockerRegistryPassword=$docker_registry_password dockerRegistryServerName=$docker_registry_server_url dockerRegistryUserName=$docker_registry_username
