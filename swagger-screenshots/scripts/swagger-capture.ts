import { chromium } from '@playwright/test';

async function main() {
  const browser = await chromium.launch({
    headless: false
  });

  const page = await browser.newPage();

  await page.goto('https://portal.developers.newpay.com.ar/');

  await page.screenshot({
    path: 'inicio.png',
    fullPage: true
  });

  await browser.close();
}

main();