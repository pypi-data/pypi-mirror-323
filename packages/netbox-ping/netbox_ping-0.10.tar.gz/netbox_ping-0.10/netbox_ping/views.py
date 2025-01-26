from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View
from dcim.models import Device, Interface, InterfaceTemplate
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.conf import settings
from django.contrib import messages
from ipam.models import Prefix, IPAddress
from ipaddress import ip_network, ip_interface
import subprocess
import concurrent.futures
from datetime import date
from django.http import JsonResponse

from .utils import UnifiedInterface, natural_keys
from .forms import InterfaceComparisonForm
from extras.models import Tag
from .models import PluginSettingsModel

config = settings.PLUGINS_CONFIG['netbox_ping']


class InterfaceComparisonView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Comparison of interfaces between a device and a device type and beautiful visualization"""
    permission_required = ("dcim.view_interface", "dcim.add_interface", "dcim.change_interface", "dcim.delete_interface")

    def get(self, request, device_id):
        device = get_object_or_404(Device.objects.filter(id=device_id))
        interfaces = device.vc_interfaces()
        if config["exclude_virtual_interfaces"]:
            interfaces = list(filter(lambda i: not i.is_virtual, interfaces))
        interface_templates = InterfaceTemplate.objects.filter(device_type=device.device_type)

        unified_interfaces = [UnifiedInterface(i.id, i.name, i.type, i.get_type_display()) for i in interfaces]
        unified_interface_templates = [
            UnifiedInterface(i.id, i.name, i.type, i.get_type_display(), i.mgmt_only, is_template=True) for i in interface_templates]

        # List of interfaces and interface templates presented in the unified format
        overall_interfaces = list(set(unified_interface_templates + unified_interfaces))
        overall_interfaces.sort(key=lambda o: natural_keys(o.name))

        comparison_templates = []
        comparison_interfaces = []
        for i in overall_interfaces:
            try:
                comparison_templates.append(unified_interface_templates[unified_interface_templates.index(i)])
            except ValueError:
                comparison_templates.append(None)

            try:
                comparison_interfaces.append(unified_interfaces[unified_interfaces.index(i)])
            except ValueError:
                comparison_interfaces.append(None)

        comparison_items = list(zip(comparison_templates, comparison_interfaces))
        return render(
            request, "netbox_ping/interface_comparison.html",
            {
                "comparison_items": comparison_items,
                "templates_count": len(interface_templates),
                "interfaces_count": len(interfaces),
                "device": device
             }
        )

    def post(self, request, device_id):
        form = InterfaceComparisonForm(request.POST)
        if form.is_valid():
            device = get_object_or_404(Device.objects.filter(id=device_id))
            interfaces = device.vc_interfaces()
            if config["exclude_virtual_interfaces"]:
                interfaces = interfaces.exclude(type__in=["virtual", "lag"])
            interface_templates = InterfaceTemplate.objects.filter(device_type=device.device_type)

            # Manually validating interfaces and interface templates lists
            add_to_device = filter(
                lambda i: i in interface_templates.values_list("id", flat=True),
                map(int, filter(lambda x: x.isdigit(), request.POST.getlist("add_to_device")))
            )
            remove_from_device = filter(
                lambda i: i in interfaces.values_list("id", flat=True),
                map(int, filter(lambda x: x.isdigit(), request.POST.getlist("remove_from_device")))
            )

            # Remove selected interfaces from the device and count them
            interfaces_deleted = Interface.objects.filter(id__in=remove_from_device).delete()[0]

            # Add selected interfaces to the device and count them
            add_to_device_interfaces = InterfaceTemplate.objects.filter(id__in=add_to_device)
            interfaces_created = len(Interface.objects.bulk_create([
                Interface(device=device, name=i.name, type=i.type, mgmt_only=i.mgmt_only) for i in add_to_device_interfaces
            ]))

            # Getting and validating a list of interfaces to rename
            fix_name_interfaces = filter(lambda i: str(i.id) in request.POST.getlist("fix_name"), interfaces)
            # Casting interface templates into UnifiedInterface objects for proper comparison with interfaces for renaming
            unified_interface_templates = [
                UnifiedInterface(i.id, i.name, i.type,i.mgmt_only, i.get_type_display()) for i in interface_templates]

            # Rename selected interfaces
            interfaces_fixed = 0
            for interface in fix_name_interfaces:
                unified_interface = UnifiedInterface(interface.id, interface.name, interface.type, interface.mgmt_only, interface.get_type_display())
                try:
                    # Try to extract an interface template with the corresponding name
                    corresponding_template = unified_interface_templates[unified_interface_templates.index(unified_interface)]
                    interface.name = corresponding_template.name
                    interface.save()
                    interfaces_fixed += 1
                except ValueError:
                    pass

            # Generating result message
            message = []
            if interfaces_created > 0:
                message.append(f"created {interfaces_created} interfaces")
            if interfaces_deleted > 0:
                message.append(f"deleted {interfaces_deleted} interfaces")
            if interfaces_fixed > 0:
                message.append(f"fixed {interfaces_fixed} interfaces")
            messages.success(request, "; ".join(message).capitalize())

            return redirect(request.path)

class PingHomeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "ipam.view_prefix"

    def get_prefix_stats(self, prefix):
        """Get statistics for a prefix"""
        # Get child IPs count using NetBox's method
        used_ips = prefix.get_child_ips().count()
        
        # Get total available IPs
        total_ips = prefix.get_available_ips().size
        
        # Calculate utilization
        utilization = round((used_ips / total_ips * 100), 2) if total_ips > 0 else 0
        
        # Debug info
        print(f"\nPrefix: {prefix.prefix}")
        print(f"Child IPs: {used_ips}")
        print(f"Total Available: {total_ips}")
        print(f"Utilization: {utilization}%")
        print("---")
        
        return {
            'total_ips': total_ips,
            'used_ips': used_ips,
            'available_ips': total_ips - used_ips,
            'utilization': utilization
        }

    def get(self, request):
        settings = PluginSettingsModel.get_settings()
        prefixes = Prefix.objects.all()
        prefix_data = []

        for prefix in prefixes:
            stats = self.get_prefix_stats(prefix)
            prefix_data.append({
                'prefix': prefix,
                'stats': stats,
                'description': prefix.description or "No description",
                'site': prefix.site.name if prefix.site else "—",
                'vrf': prefix.vrf.name if prefix.vrf else "Global",
                'tenant': prefix.tenant.name if prefix.tenant else "—",
            })

        return render(request, 'netbox_ping/ping_home.html', {
            'prefix_data': prefix_data,
            'tab': 'main',
            'model': Prefix,
            'table': None,
            'actions': ('add', 'import', 'export', 'bulk_edit', 'bulk_delete'),
            'update_tags': settings.update_tags,
        })

    def post(self, request):
        settings = PluginSettingsModel.get_settings()
        settings.update_tags = request.POST.get('update_tags') == 'true'
        settings.save()
        return JsonResponse({'status': 'success'})

class PingSubnetView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """View for pinging existing IPs in a subnet"""
    permission_required = "ipam.view_prefix"

    def ping_ip(self, ip):
        """Ping a single IP address"""
        try:
            # Try multiple pings to be more accurate
            for _ in range(2):  # Try twice
                result = subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)], 
                                    capture_output=True, 
                                    timeout=2)
                if result.returncode == 0:
                    return str(ip), True
            return str(ip), False
        except:
            return str(ip), False

    def get(self, request, prefix_id):
        # Get update_tags parameter
        update_tags = request.GET.get('update_tags', 'true').lower() == 'true'
        
        prefix = get_object_or_404(Prefix, id=prefix_id)
        messages.info(request, f"🔍 Starting status check for subnet {prefix.prefix}")

        try:
            online_tag = Tag.objects.get(slug='online')
            offline_tag = Tag.objects.get(slug='offline')
        except Tag.DoesNotExist:
            messages.error(request, "Required tags not found. Please initialize the plugin first.")
            return redirect('plugins:netbox_ping:ping_home')

        # Get all child IPs using NetBox's method
        all_ips = prefix.get_child_ips()
        
        if not all_ips.exists():
            messages.warning(request, "No child IPs found in this subnet")
            return redirect('ipam:prefix', pk=prefix_id)

        status_changes = []
        processed_ips = set()  # Keep track of processed IPs

        # Ping all IPs
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_ip = {
                executor.submit(self.ping_ip, str(ip_interface(ip.address).ip)): ip 
                for ip in all_ips
            }
            
            for future in concurrent.futures.as_completed(future_to_ip):
                ip_obj = future_to_ip[future]
                ip_str, is_alive = future.result()
                
                # Skip if we've already processed this IP
                if ip_str in processed_ips:
                    continue
                processed_ips.add(ip_str)

                # Initialize custom_field_data if needed
                if not ip_obj.custom_field_data:
                    ip_obj.custom_field_data = {}
                
                old_status = ip_obj.custom_field_data.get('Up_Down', None)
                ip_obj.custom_field_data['Up_Down'] = is_alive
                
                if is_alive:
                    if update_tags:
                        ip_obj.tags.remove(offline_tag)
                        ip_obj.tags.add(online_tag)
                    status = "🟢 up"
                else:
                    if update_tags:
                        ip_obj.tags.remove(online_tag)
                        ip_obj.tags.add(offline_tag)
                    status = "🔴 down"
                
                ip_obj.save()
                
                # Record status changes
                if old_status is None:
                    status_changes.append(f"{ip_str}: {status} (initial check)")
                elif old_status != is_alive:
                    status_changes.append(f"{ip_str}: {status}")

        # Show summary message
        if status_changes:
            messages.success(request, f"✅ Status check complete - Changes detected:\n" + "\n".join(status_changes))
        else:
            messages.success(request, f"✅ Status check complete - No changes detected")

        return redirect('ipam:prefix', pk=prefix_id)

def get_existing_ip(ip_str, prefix_length):
    """Helper function to check if IP exists (case-insensitive)"""
    try:
        return IPAddress.objects.get(address__iexact=f"{ip_str}/{prefix_length}")
    except IPAddress.DoesNotExist:
        return None

class ScanSubnetView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """View for scanning entire subnet and adding all discovered IPs"""
    permission_required = "ipam.view_prefix"

    def ping_ip(self, ip):
        """Ping a single IP address"""
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)], 
                                  capture_output=True, 
                                  timeout=2)
            return str(ip), result.returncode == 0
        except:
            return str(ip), False

    def get(self, request, prefix_id):
        prefix = get_object_or_404(Prefix, id=prefix_id)
        messages.info(request, f"Initiating full scan of subnet {prefix.prefix}")

        prefix_length = prefix.prefix.prefixlen

        try:
            online_tag = Tag.objects.get(slug='online')
            offline_tag = Tag.objects.get(slug='offline')
            auto_discovered_tag = Tag.objects.get(slug='auto-discovered')
        except Tag.DoesNotExist:
            messages.error(request, "Required tags not found. Please initialize the plugin first.")
            return redirect('plugins:netbox_ping:ping_home')

        network = ip_network(prefix.prefix)
        discovered_ips = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            hosts = list(network.hosts()) if network.prefixlen < 31 else list(network)
            future_to_ip = {executor.submit(self.ping_ip, ip): ip for ip in hosts}
            
            for future in concurrent.futures.as_completed(future_to_ip):
                ip_str, is_alive = future.result()
                
                if is_alive:
                    # Check if IP exists (case-insensitive)
                    ip_obj = get_existing_ip(ip_str, prefix_length)
                    
                    if ip_obj:
                        # Update existing IP
                        ip_obj.custom_field_data['Up_Down'] = True
                        ip_obj.tags.remove(offline_tag)
                        ip_obj.tags.add(online_tag)
                        ip_obj.save()
                        messages.info(request, f"Updated IP {ip_str} status to up")
                    else:
                        # Add new IP
                        discovered_ips.append(ip_str)
                        try:
                            ip_obj = IPAddress.objects.create(
                                address=f"{ip_str}/{prefix_length}",
                                status='active',
                                custom_field_data={
                                    'Up_Down': True,
                                    'Auto_discovered': str(date.today())
                                }
                            )
                            ip_obj.tags.add(online_tag)
                            ip_obj.tags.add(auto_discovered_tag)
                            messages.success(request, f"Added new IP {ip_str}")
                        except Exception as e:
                            messages.error(request, f"Failed to add IP {ip_str}: {str(e)}")

        if discovered_ips:
            messages.success(request, f"Discovered {len(discovered_ips)} new IPs: {', '.join(discovered_ips)}")
        else:
            messages.info(request, "No new IPs discovered")

        return redirect('ipam:prefix', pk=prefix_id)

class InitializePluginView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """View for manually initializing plugin custom fields and tags"""
    permission_required = "ipam.view_prefix"

    def get(self, request):
        from .plugin import initialize_plugin
        try:
            initialize_plugin()
            messages.success(request, "Successfully initialized custom fields and tags!")
        except Exception as e:
            messages.error(request, f"Failed to initialize: {str(e)}")
        
        return redirect('plugins:netbox_ping:ping_home')

class ScanAllView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """View for scanning all prefixes"""
    permission_required = "ipam.view_prefix"

    def ping_ip(self, ip):
        """Ping a single IP address"""
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)], 
                                  capture_output=True, 
                                  timeout=2)
            return str(ip), result.returncode == 0
        except Exception as e:
            print(f"Error pinging {ip}: {str(e)}")
            return str(ip), False

    def get(self, request):
        messages.info(request, "Starting scan of all prefixes...")
        
        try:
            online_tag = Tag.objects.get(slug='online')
            offline_tag = Tag.objects.get(slug='offline')
            auto_discovered_tag = Tag.objects.get(slug='auto-discovered')
        except Tag.DoesNotExist:
            messages.error(request, "Required tags not found. Please initialize the plugin first.")
            return redirect('plugins:netbox_ping:ping_home')

        total_discovered = 0
        total_prefixes = Prefix.objects.count()
        current_prefix = 0

        for prefix in Prefix.objects.iterator():
            current_prefix += 1
            messages.info(request, f"Scanning prefix {current_prefix}/{total_prefixes}: {prefix.prefix}")
            
            try:
                network = ip_network(prefix.prefix)
                prefix_length = prefix.prefix.prefixlen
                
                # Get list of hosts to scan
                hosts = list(network.hosts()) if network.prefixlen < 31 else list(network)
                
                # Skip if too many hosts to scan
                if len(hosts) > 1000:
                    messages.warning(request, f"Skipping {prefix.prefix} - too many hosts ({len(hosts)})")
                    continue

                # Scan the subnet
                with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                    future_to_ip = {executor.submit(self.ping_ip, ip): ip for ip in hosts}
                    
                    for future in concurrent.futures.as_completed(future_to_ip):
                        try:
                            ip_str, is_alive = future.result()
                            
                            if is_alive:
                                # Check if IP exists (case-insensitive)
                                ip_obj = get_existing_ip(ip_str, prefix_length)
                                
                                if ip_obj:
                                    # Update existing IP
                                    ip_obj.custom_field_data['Up_Down'] = True
                                    ip_obj.tags.remove(offline_tag)
                                    ip_obj.tags.add(online_tag)
                                    ip_obj.save()
                                else:
                                    # Add new IP
                                    ip_obj = IPAddress.objects.create(
                                        address=f"{ip_str}/{prefix_length}",
                                        status='active',
                                        custom_field_data={
                                            'Up_Down': True,
                                            'Auto_discovered': str(date.today())
                                        }
                                    )
                                    ip_obj.tags.add(online_tag)
                                    ip_obj.tags.add(auto_discovered_tag)
                                    total_discovered += 1
                                    messages.info(request, f"Discovered new IP: {ip_str}")
                        except Exception as e:
                            messages.error(request, f"Error processing {ip_str}: {str(e)}")
                            continue

            except Exception as e:
                messages.error(request, f"Error scanning prefix {prefix.prefix}: {str(e)}")
                continue

        messages.success(request, f"✅ Completed scanning all prefixes. Discovered {total_discovered} new IPs.")
        return redirect('plugins:netbox_ping:ping_home')

class UpdateSettingsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "ipam.view_prefix"

    def post(self, request):
        settings = PluginSettingsModel.get_settings()
        settings.update_tags = request.POST.get('update_tags') == 'true'
        settings.save()
        return JsonResponse({'status': 'success'})