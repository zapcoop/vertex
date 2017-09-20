// @flow
import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import registerServiceWorker from './registerServiceWorker';

import BrowserProtocol from 'farce/lib/BrowserProtocol';
import queryMiddleware from 'farce/lib/queryMiddleware';
import createFarceRouter from 'found/lib/createFarceRouter';
import createRender from 'found/lib/createRender';
import { Resolver } from 'found-relay';
// import { Network } from 'relay-local-schema';
import { Environment, RecordSource, Store } from 'relay-runtime';

import routes from './routes';

(function() {
  let bodyElement = document.querySelector('body');
  if (bodyElement !== null) {
    bodyElement.classList.add('loading');
  }
  document.addEventListener('readystatechange', function() {
    if (document.readyState === 'complete') {
      let bodyElement = document.querySelector('body');
      let loaderElement = document.querySelector('#initial-loader');
      if (bodyElement !== null) {
        bodyElement.classList.add('loaded');
      }
      setTimeout(function() {
        if (bodyElement !== null && loaderElement !== null) {
          bodyElement.removeChild(loaderElement);
          bodyElement.classList.remove('loading', 'loaded');
        }
      }, 200);
    }
  });
})();

const environment = new Environment({
  // network: Network.create({ schema }),
  store: new Store(new RecordSource()),
});

const Router = createFarceRouter({
  historyProtocol: new BrowserProtocol(),
  historyMiddlewares: [queryMiddleware],
  routeConfig: routes,

  render: createRender({}),
});

const mountNode = document.getElementById('root');

ReactDOM.render(<Router resolver={new Resolver(environment)} />, mountNode);

registerServiceWorker();
