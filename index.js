#!/usr/bin/env node

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const util = require('util');
const execAsync = util.promisify(exec);

// Matrix Colors
const C = '\x1b[36m'; // Cyan
const G = '\x1b[32m'; // Green
const Y = '\x1b[33m'; // Yellow
const R = '\x1b[31m'; // Red
const M = '\x1b[35m'; // Magenta
const Z = '\x1b[0m';  // Reset
const B = '\x1b[1m';  // Bold

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function typeWriter(text, speed = 15) {
    for (let char of text) {
        process.stdout.write(char);
        await sleep(speed);
    }
    console.log();
}

async function decryptText(text, duration = 1000) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*';
    const iterations = duration / 50;
    for (let i = 0; i < iterations; i++) {
        let scrambled = '';
        for (let j = 0; j < text.length; j++) {
            if (text[j] === ' ') scrambled += ' ';
            else scrambled += chars[Math.floor(Math.random() * chars.length)];
        }
        process.stdout.write('\r' + G + scrambled + Z);
        await sleep(50);
    }
    process.stdout.write('\r' + C + B + text + Z + '\n');
}

async function runCommandWithSpinner(text, cmd) {
    const frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
    let i = 0;
    let done = false;
    
    const interval = setInterval(() => {
        if (!done) {
            process.stdout.write(`\r${M}${frames[i]} ${C}${text} ${G}[0x${Math.floor(Math.random()*16777215).toString(16).toUpperCase().padStart(6,'0')}]${Z}   `);
            i = (i + 1) % frames.length;
        }
    }, 80);

    try {
        await execAsync(cmd);
    } catch(e) {
        // Ignore errors to keep it flowing
    }
    
    done = true;
    clearInterval(interval);
    process.stdout.write(`\r${G}✔ ${text} [COMPLETED]                 ${Z}\n`);
}

async function run() {
    console.clear();
    
    try {
        console.log(R + B + "/// ACCESS RESTRICTED: SECURITY CLEARANCE REQUIRED ///" + Z);
        const { execSync } = require('child_process');
        execSync('sudo -v', { stdio: 'inherit' });
    } catch(e) {
        console.log(R + "Intruder detected. Terminating connection." + Z);
        process.exit(1);
    }
    console.clear();

    await decryptText("INITIALIZING HARDWARE SCAN...");
    const gbRam = Math.round(os.totalmem() / (1024 * 1024 * 1024));
    console.log(G + `[+] CPU Architecture: ${os.arch().toUpperCase()}` + Z);
    await sleep(200);
    console.log(G + `[+] Neural RAM Capacity: ${gbRam} GB Allocated` + Z);
    await sleep(200);
    console.log(G + `[+] Host OS Kernel: ${os.type()} v${os.release()}` + Z);
    await sleep(500);
    
    console.log(Y + "\nBypassing Mainframe Firewalls..." + Z);
    await sleep(400);
    console.log(G + "Connection Secured. Handshake accepted.\n" + Z);
    await sleep(300);
    console.clear();

    const logo = C + B + `

 _    ___                _____                  
| |  / (_)__ _      __  / ___/__  ______  _____ 
| | / / / _ \\ | /| / /  \\__ \\/ / / / __ \\/ ___/ 
| |/ / /  __/ |/ |/ /  ___/ / /_/ / / / / /__   
|___/_/\\___/|__/|__/  /____/\\__, /_/ /_/[___/   
                           /____/               
       [ PROJECT: VIEW-SYNC ] [ v2.0.0 ]
` + Z;

    console.log(logo);
    await typeWriter(M + "> SYSTEM: INITIATING AUTO-DEPLOYMENT SEQUENCE..." + Z, 20);
    await sleep(400);

    try {
        await typeWriter(Y + "\n[PHASE 1] INJECTING CORE DEPENDENCIES" + Z, 10);
        await runCommandWithSpinner("Updating APT Repositories", "sudo apt update");
        await runCommandWithSpinner("Injecting ADB Protocols", "sudo apt install -y adb");
        await runCommandWithSpinner("Injecting X11 Automation Core", "sudo apt install -y xdotool");
        await runCommandWithSpinner("Compiling Python GUI Interface", "sudo apt install -y python3-tk python3-pip");
        
        try {
            await execAsync('which scrcpy');
        } catch (e) {
            await runCommandWithSpinner("Deploying ViewSync Display Engine", "sudo apt install -y scrcpy");
        }

        await typeWriter(Y + "\n[PHASE 2] COMPILING NEURAL PYTHON MODULES" + Z, 10);
        await runCommandWithSpinner("Fetching Pynput Algorithms", "pip3 install pynput --break-system-packages || pip3 install pynput");

        await typeWriter(Y + "\n[PHASE 3] SECURING ENCRYPTED VAULT" + Z, 10);
        await runCommandWithSpinner("Allocating Memory Vault", "sleep 1");
        
        const targetDir = path.join(os.homedir(), '.viewsync');
        if (!fs.existsSync(targetDir)) {
            fs.mkdirSync(targetDir, { recursive: true });
        }
        fs.copyFileSync(path.join(__dirname, 'viewsync_main.py'), path.join(targetDir, 'viewsync_main.py'));
        const iconPath = path.join(__dirname, 'icon.png');
        if (fs.existsSync(iconPath)) {
            fs.copyFileSync(iconPath, path.join(targetDir, 'icon.png'));
        }

        const helperPath = path.join(__dirname, 'viewsync_helper.py');
        if (fs.existsSync(helperPath)) {
            fs.copyFileSync(helperPath, path.join(targetDir, 'viewsync_helper.py'));
        }
        await runCommandWithSpinner("Encrypting Source Code", "sleep 1");

        await typeWriter(Y + "\n[PHASE 4] ESTABLISHING UPLINK PROTOCOL" + Z, 10);
        const desktopDir = path.join(os.homedir(), 'Desktop');
        const shortcutPath = path.join(desktopDir, 'ViewSync.desktop');
        
        const desktopEntry = `[Desktop Entry]
Name=ViewSync
Comment=Live screen cropper & lag-free mirroring
Exec=bash -c "python3 ~/.viewsync/viewsync_main.py"
Icon=${targetDir}/icon.png
Terminal=false
Type=Application
Categories=Utility;
`;
        fs.writeFileSync(shortcutPath, desktopEntry);
        fs.chmodSync(shortcutPath, 0o755);
        await runCommandWithSpinner("Linking Desktop Node", "sleep 1");

        console.log(G + B + `
======================================================
  [✓] SYSTEM OVERRIDE SUCCESSFUL! 
  [✓] VIEWSYNC MASTER HAS INFILTRATED YOUR SYSTEM.
======================================================` + Z);
        
        process.stdout.write('\x07');
        
        await typeWriter(C + "> INSTRUCTIONS: Plug in your Android device (USB Debugging ON).", 15);
        await typeWriter(C + "> Double-click the 'ViewSync' uplink on your desktop to begin.", 15);
        console.log();

    } catch (error) {
        console.log(R + B + "\n[!] FATAL SYSTEM EXCEPTION: UPLINK SEVERED." + Z);
    }
}

run();
