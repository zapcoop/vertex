import makeRouteConfig from 'found/lib/makeRouteConfig';
import Route from 'found/lib/Route';
import React from 'react';

import App from './App';

export default makeRouteConfig(<Route path="/" Component={App} />);
