import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import Recent from './Recent';
import { Checks, ChecksListWithData, CheckForm } from './Checks';

import './index.css';
import { Router, Route, IndexRoute, Link, hashHistory } from 'react-router';

ReactDOM.render((
  <Router history={hashHistory}>
    <Route path="/" component={App}>
      <IndexRoute component={Recent} />
      <Route path="checks" component={Checks}>
        <IndexRoute component={ChecksListWithData} />
        <Route path=":id/edit" component={CheckForm} />
      </Route>
    </Route>
  </Router>
), document.getElementById('root'))