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
  await page.setViewport({width: 1300, height: 2050, deviceScaleFactor: 2});
  await page.screenshot({path: 'map_faroe.png'});

  // optimize the PNG file
  log.info('imagemin', 'Optimizing map_faroe.png ...');

  await imagemin(['map_faroe.png'], {
      destination: 'build/',
      plugins: [
          imageminPngquant({
              quality: [0.6, 0.8]
          })
      ]
  });

  await fs.rm('map_faroe.png');
  await fs.rename('build/map_faroe.png', 'map_faroe.png');

  await browser.close();
  log.info('Done');
})();
