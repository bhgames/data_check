import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import Recent from './Recent';
import { Checks, ChecksListWithData, CheckFormWithData } from './Checks';
import { Rules, RulesListWithData, RuleFormWithData } from './Rules';
import { JobTemplates, JobTemplatesListWithData, JobTemplateFormWithData } from './JobTemplates';
import { DataSources, DataSourcesListWithData, DataSourceFormWithData } from './DataSources';

import './index.css';
import { Router, Route, IndexRoute, hashHistory } from 'react-router';

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
      <Route path="data_sources" component={DataSources}>
        <IndexRoute component={DataSourcesListWithData} />
        <Route path=":id/edit" component={DataSourceFormWithData} />
      </Route>
    </Route>
  </Router>
), document.getElementById('root'))