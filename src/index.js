import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import Recent from './Recent';
import { Checks, ChecksListWithData, CheckFormWithData } from './Checks';
import { Rules, RulesListWithData, RuleFormWithData } from './Rules';
import { JobTemplates, JobTemplatesListWithData, JobTemplateFormWithData } from './JobTemplates';

import './index.css';
import { Router, Route, IndexRoute, Link, hashHistory } from 'react-router';

ReactDOM.render((
  <Router history={hashHistory}>
    <Route path="/" component={App}>
      <IndexRoute component={Recent} />
      <Route path="checks" component={Checks}>
        <IndexRoute component={ChecksListWithData} />
        <Route path=":id/edit" component={CheckFormWithData} />
      </Route>
      <Route path="rules" component={Rules}>
        <IndexRoute component={RulesListWithData} />
        <Route path=":id/edit" component={RuleFormWithData} />
      </Route>
      <Route path="job_templates" component={JobTemplates}>
        <IndexRoute component={JobTemplatesListWithData} />
        <Route path=":id/edit" component={JobTemplateFormWithData} />
      </Route>
    </Route>
  </Router>
), document.getElementById('root'))