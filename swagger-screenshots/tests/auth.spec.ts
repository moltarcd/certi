import { test as setup } from '@playwright/test';

setup('authenticate', async ({ page }) => {
  await page.goto('https://portal.developers.newpay.com.ar/');

  await page.getByRole('button', { name: 'Iniciar Sesión' }).click();

  await page.locator('#email').fill('banelcoportalprod@yopmail.com');
  await page.getByRole('textbox', { name: '••••••••' }).fill('634Prisma01!');

  await page.getByRole('button', { name: 'Ingresar' }).click();

  await page.getByRole('button', { name: 'siguiente' }).click();

  await page.context().storageState({
    path: 'playwright/.auth/user.json'
  });
});