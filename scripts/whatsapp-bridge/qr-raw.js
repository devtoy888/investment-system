#!/usr/bin/env node
/**
 * WhatsApp QR - outputs raw pairing code + HTML QR page
 */
import { makeWASocket, useMultiFileAuthState, fetchLatestBaileysVersion } from '@whiskeysockets/baileys';
import pino from 'pino';
import fs from 'fs';

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
      // Save the raw QR code
      process.stdout.write('\n===== RAW_QR_START =====\n');
      process.stdout.write(qr + '\n');
      process.stdout.write('===== RAW_QR_END =====\n');
    }

    if (connection === 'open') {
      process.stdout.write('\n✓ WhatsApp connected successfully!\n');
      process.exit(0);
    }

    if (connection === 'close') {
      const reason = lastDisconnect?.error?.output?.statusCode;
      process.exit(reason ? 1 : 1);
    }
  });
}

main().catch(e => {
  process.exit(1);
});
