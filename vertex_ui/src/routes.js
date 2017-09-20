import makeRouteConfig from 'found/lib/makeRouteConfig';
import Route from 'found/lib/Route';
import React from 'react';

// import App from './App';
import DefaultLayout from './layouts/DefaultLayout';

export default makeRouteConfig(<Route path="/" Component={DefaultLayout} />);
