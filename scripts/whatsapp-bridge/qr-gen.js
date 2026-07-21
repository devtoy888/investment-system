#!/usr/bin/env node
/**
 * WhatsApp QR code generator - outputs QR as ASCII + pairing code
 */
import { makeWASocket, useMultiFileAuthState, fetchLatestBaileysVersion } from '@whiskeysockets/baileys';
import pino from 'pino';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const sessionDir = process.argv[2] || '/opt/data/whatsapp/session';

async function main() {
  fs.mkdirSync(sessionDir, { recursive: true });

  const { state, saveCreds } = await useMultiFileAuthState(sessionDir);
  const { version } = await fetchLatestBaileysVersion();

  const sock = makeWASocket({
    version,
    auth: state,
    logger: pino({ level: 'silent' }),
    printQRInTerminal: false,
    browser: ['Hermes Agent', 'Chrome', '22'],
  });

  let qrDisplayed = false;

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', async (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr && !qrDisplayed) {
      qrDisplayed = true;
      try {
        const QRCode = (await import('qrcode-terminal')).default;
        QRCode.generate(qr, { small: false });
      } catch (e) {
        // fallback
      }
      console.log('\n===== QR CODE RAW (copy this) =====');
      console.log(qr);
      console.log('===== END QR CODE =====\n');
      console.log('📱 Open WhatsApp > Settings > Linked Devices > Link a Device');
      console.log('➡️ Scan the QR code above ^^^');
    }

    if (connection === 'open') {
      console.log('\n✓ WhatsApp connected successfully!');
      process.exit(0);
    }

    if (connection === 'close') {
      const reason = lastDisconnect?.error?.output?.statusCode;
      console.log('\n✗ Connection closed:', reason || 'unknown');
      process.exit(1);
    }
  });
}

main().catch(e => {
  console.error('Error:', e);
  process.exit(1);
});
