import React from 'react';
import './App.css';
import { Table } from 'react-bootstrap';

  // Put sidebar here.
function Recent() {
  return (
    <div>
      <Table responsive striped bordered condensed hover>
        <thead>
          <tr>
            <th>Run ID</th>
            <th>Template Name</th>
            <th>Status</th>
            <th>Scheduled At</th>
            <th>Run At</th>
            <th>Failed At</th>
            <th>Cancelled At</th>
            <th>Rejected At</th>
            <th>Finished At</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>1</td>
            <td>Billy the Job</td>
            <td>FAILED</td>
            <td>2016-10-31 05:00</td>
            <td>2016-10-31 05:00</td>
            <td></td>
            <td></td>
            <td></td>
            <td>2016-10-31 05:00</td>
          </tr>
        </tbody>
      </Table> 
    </div>
  );
}

export default Recent;
