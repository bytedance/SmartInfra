"""
// Copyright (c) 2024 Bytedance Ltd. and/or its affiliates
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
"""
from django.urls import path
from salt import views


urlpatterns = [
    path('index/', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('', views.login, name='login'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('authenticate_user/', views.authenticate_user, name='authenticate_user'),
    path('salt_masters/', views.list_masters, name='salt_masters'),
    path('create_salt/', views.create_salt, name='create_salt'),
    path('del_salt/', views.del_salt, name='del_salt'),
    path('check_salt_master/', views.check_salt_master, name='check_salt_master'),
    path('check_sftp/', views.check_sftp, name='check_sftp'),
    path('shell_template/', views.list_shell_template, name='shell_template'),
    path('create_shell_template/', views.create_shell_template, name='create_shell_template'),
    path('del_shell_template/', views.del_shell_template, name='del_shell_template'),
    path('resource_group/', views.list_resource_group, name='resource_group'),
    path('create_resource_group/', views.create_resource_group, name='create_resource_group'),
    path('del_resource_group/', views.del_resource_group, name='del_resource_group'),
    path('ro_setup/', views.list_ro_setup, name='ro_setup'),
    path('create_acl/', views.create_acl, name='create_acl'),
    path('users_list/', views.list_users, name='users_list'),
    path('create_user_relationship/', views.create_user_relationship, name='create_user_relationship'),
    path('del_user/', views.del_user, name='del_user'),
    path('hosts/', views.list_hosts, name='hosts'),
    path('setup_host/', views.setup_host, name='setup_host'),
    path('refresh_minion/', views.refresh_minion, name='refresh_minion'),
    path('read_file/', views.read_file, name='read_file'),
    path('host_group/', views.list_host_group, name='host_group'),
    path('create_host_group/', views.create_host_group, name='create_host_group'),
    path('download_hg/', views.download_hg, name='download_hg'),
    path('del_host_group/', views.del_host_group, name='del_host_group'),
    path('show_selected_host_group/', views.show_selected_host_group, name='show_selected_host_group'),
    path('search_available_host/', views.search_available_host, name='search_available_host'),
    path('create_shell_task/', views.create_shell_task, name='create_shell_task'),
    path('list_tasks/', views.list_tasks, name='list_tasks'),
    path('approve_task/', views.approve_task, name='approve_task'),
    path('withdraw_task/', views.withdraw_task, name='withdraw_task'),
    path('stop_task/', views.stop_task, name='stop_task'),
    path('get_task_info/', views.get_task_info, name='get_task_info'),
    path('download_execute_result/', views.download_execute_result, name='download_execute_result'),
    path('show_message/', views.show_message, name='show_message'),
    path('audit_info/', views.audit_info, name='audit_info'),
    path('authenticate_mgmt/', views.authenticate_mgmt, name='authenticate_mgmt'),
    path('oauth/callback/', views.callback_oauth, name='callback_oauth'),
    path('update_authn/', views.update_authn, name='update_authn'),
    path('upload_transfer_file/', views.upload_transfer_file, name='upload_transfer_file'),
    path('delete_transfer_file/', views.delete_transfer_file, name='delete_transfer_file'),
    path('get_audit_info/', views.get_audit_info, name='get_audit_info'),
    path('get_hosts/', views.get_hosts, name='get_hosts'),
    path('reject_task/', views.reject_task, name='reject_task'),
    path('check_ldap/', views.check_ldap, name='check_ldap'),
    path('sub_template/<int:id>/', views.list_sub_st, name='list_sub_st'),
    path('create_sub_st/', views.create_sub_st, name='create_sub_st'),
    path('del_sub_st/', views.del_sub_st, name='del_sub_st'),
    path('get_all_users/', views.get_all_users, name='get_all_users'),
    path('grant_st/', views.grant_st, name='grant_st'),

]
