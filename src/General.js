import React, { Component } from 'react';
import { LinkContainer } from 'react-router-bootstrap';
import { Button, Table, ControlLabel, FormControl, FormGroup, HelpBlock } from 'react-bootstrap';

export class WithData extends Component {

  constructor(props) {
    super(props);

    this.state = { data: [] };

    let headers = new Headers();
    headers.append('Content-Type', 'application/json');

    let params = { method: 'GET',
                   headers: headers,
                   mode: 'cors'
                 };

    let get = new Request('http://localhost:5000/' + props.resource);
    let that = this;

    fetch(get, params).then(function(response) {
      return response.json();
    }).then(function(json) {
      that.setState({ data: json })
    })
  }

  render() {
    const childrenWithProps = React.Children.map(this.props.children,
      (child) => React.cloneElement(child, {
        data: this.state.data
      })
    );

    return <div>{childrenWithProps}</div>
  }
}

WithData.propTypes = {
  resource: React.PropTypes.string.isRequired
}

export function List({ columnNames, columns, baseResource, data }) {

  // Stringify JSON objects(like check_metadata or other metadata objects in a row)
  for(let row of data) {
    for (let col of columns) {
      if(typeof row[col] === 'object') {
        row[col] = JSON.stringify(row[col]);
      }
    }
  }

  return (
    <div>

      <LinkContainer to={ baseResource + '/new/edit'}>
        <Button bsStyle="primary">New</Button>
      </LinkContainer>

      <Table responsive striped bordered condensed hover>
        <thead>
          <tr>
            {columnNames.map(name =>
              <th key={name}>{name}</th>
            )}
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {data.map(row => 
            <tr key={row.id}>
              {columns.map(col =>
                <td key={col}>{row[col]}</td>
              )}
              <td>
                <LinkContainer to={'/' + baseResource + '/' + row.id + '/edit'}>
                  <Button>Edit</Button>
                </LinkContainer>
                <Button>Delete</Button>
              </td>
            </tr>
          )}
        </tbody>
      </Table> 
    </div>
  );
}

List.defaultProps = {
  data: []
};
