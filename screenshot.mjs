#!/usr/bin/env node
import puppeteer from 'puppeteer';

import path from 'path';
import fs from 'fs/promises';
import log from 'npmlog';

import imagemin from 'imagemin';
import imageminPngquant from 'imagemin-pngquant';

import {setTimeout} from "timers/promises";

const url = 'http://localhost:3000/faroe';

log.info('Rendering', `<${url}> ...`);

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  page.on('requestfinished', (req) => {
    log.info('Response', `<${req.url()}>`);
  });

  const then = Date.now();
  await page.goto(url, {waitUntil: 'networkidle0'});
  const took = Date.now() - then;

  log.info(`Page loaded`, `in ${took} ms`);
  // await new Promise(resolve => setTimeout(resolve, 5000));

  log.info('Taking a screenshot');
  await page.setViewport({width: 1310, height: 2291, deviceScaleFactor: 2});
  await page.screenshot({path: 'map_faroe.png'});

  log.info('Taking a screenshot with lang=pl');
  await page.evaluate(() => {
    document.body.setAttribute('lang', 'pl');
  });
  await setTimeout(1000); // give some non-Latin fonts a chance to load
  await page.screenshot({path: 'map_faroe_pl.png'});

  await browser.close();
  log.info('Done');
})();
