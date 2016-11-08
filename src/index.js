import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import Recent from './Recent';
import { Checks, ChecksList, NewCheckForm } from './Checks';

import './index.css';
import { Router, Route, IndexRoute, Link, hashHistory } from 'react-router';

ReactDOM.render((
  <Router history={hashHistory}>
    <Route path="/" component={App}>
      <IndexRoute component={Recent} />
      <Route path="checks" component={Checks}>
        <IndexRoute component={ChecksList} />
        <Route path="new" component={NewCheckForm} />
      </Route>
    </Route>
  </Router>
), document.getElementById('root'))