#!/usr/bin/env node
import puppeteer from 'puppeteer';
import log from 'npmlog';
import {setTimeout} from "node:timers/promises";

const url = 'http://localhost:3000/faroe';

log.info('Rendering', `<${url}> ...`);

(async () => {
  const browser = await puppeteer.launch({
    // https://developer.chrome.com/articles/new-headless/
    headless: "new"
  });
  const page = await browser.newPage();

  page.on('requestfinished', (req) => {
    log.info('Response', `<${req.url()}>`);
  });

  const then = Date.now();
  await page.goto(url, {waitUntil: 'networkidle0'});
  const took = Date.now() - then;

  log.info(`Page loaded`, `in ${took} ms`);
  await setTimeout(250); // allow all things to render

  log.info('Taking a screenshot');
  // Page size:  {width: 1560, height: 2419}
  await page.setViewport({width: 1560, height: 2419, deviceScaleFactor: 2});
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
