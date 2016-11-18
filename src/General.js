import React, { Component } from 'react';
import { LinkContainer } from 'react-router-bootstrap';
import { Button, Table, ControlLabel, FormControl, FormGroup, HelpBlock } from 'react-bootstrap';
import { withRouter } from 'react-router';
import './App.css';

/*

  General File contains a lot of the elements used to do the various REST functions
  for each of the resources. Then each Resource's file.js customizes these elements to display
  what they desire for that element.

*/

export class WithData extends Component {

  constructor(props) {
    super(props);
    this.onServerDataChanged();
  }

  onServerDataChanged() {
    let headers = new Headers();
    headers.append('Content-Type', 'application/json');

    let params = { method: 'GET',
                   headers: headers,
                   mode: 'cors'
                 };

    let get = new Request('http://localhost:5000/' + this.props.baseResource);
    let that = this;

    fetch(get, params).then(function(response) {
      return response.json();
    }).then(function(json) {
      that.setState({ data: json })
    })
  }

  deleteDataItem(id) {
    let headers = new Headers();
    headers.append('Content-Type', 'application/json');

    let params = { method: 'DELETE',
                   headers: headers,
                   mode: 'cors'
                 };

    let del = new Request('http://localhost:5000/' + this.props.baseResource + '/' + id);

    let that = this;
    fetch(del, params).then(function(response) {
      that.onServerDataChanged();
    })
  }

  render() {
    if (this.state) {
      const childrenWithProps = React.Children.map(this.props.children,
        (child) => React.cloneElement(child, {
          data: this.state.data,
          baseResource: this.props.baseResource,
          deleteDataItem: this.deleteDataItem.bind(this)
        })
      );

      return <div>{childrenWithProps}</div>
    } else {
      return <div>Loading...</div>
    }
  }
}

WithData.propTypes = {
  baseResource: React.PropTypes.string.isRequired
}

export function List({ columnNames, columns, baseResource, data, deleteDataItem, onSelectHandler, selectedRows, excludedRowIds, chromeless }) {
  let deleteHandler = (row) => { deleteDataItem(row.id) };

  let handler = null;
  if(onSelectHandler) {    
    handler = (row) => {
      onSelectHandler(row);
    };
  } else {
    handler = (row) => { }
  }

  let selectedStyleHandler = (row) => {
    if(selectedRows && selectedRows.find((r) => { return r.id == row.id })) {
      return "selected";
    }
  };

  let rowIds = data.map((r) => { return r.id });
  let displayedRows = data.filter((r) => { return !excludedRowIds || !excludedRowIds.includes(rowIds[data.indexOf(r)])});

  let buttons = (row) => { 
                  return chromeless ? null : <td>
                    <LinkContainer to={'/' + baseResource + '/' + row.id + '/edit'}>
                      <Button>Edit</Button>
                    </LinkContainer>
                    <Button onClick={deleteHandler.bind(null, row)}>Delete</Button>
                  </td> 
                };
                
  let buttonHeader = chromeless ? null : <th>Actions</th>;

  let newButton = chromeless ? null : <LinkContainer to={ baseResource + '/new/edit'}>
        <Button bsStyle="primary">New</Button>
      </LinkContainer>;
  

  return (
    <div>
      {newButton}
      <Table responsive striped bordered condensed hover>
        <thead>
          <tr>
            {columnNames.map(name =>
              <th key={name}>{name}</th>
            )}
            {buttonHeader}
          </tr>
        </thead>
        <tbody>
          {displayedRows.map(row => 
            <tr key={row.id} onClick={handler.bind(this, row)} className={selectedStyleHandler(row)}>
              {columns.map(col =>
                <td key={col}>{typeof row[col] === 'object' ? JSON.stringify(row[col]) : row[col]}</td>
              )}
              {buttons(row)}
            </tr>
          )}
        </tbody>
      </Table> 
    </div>
  );
}

List.propTypes = {
  data: React.PropTypes.arrayOf(React.PropTypes.object).isRequired,
  columnNames: React.PropTypes.arrayOf(React.PropTypes.string).isRequired,
  columns: React.PropTypes.arrayOf(React.PropTypes.string).isRequired,
  baseResource: React.PropTypes.string.isRequired,
  deleteDataItem: React.PropTypes.func.isRequired,
  onSelectHandler: React.PropTypes.func,
  selectedRows: React.PropTypes.array,
  excludedRowIds: React.PropTypes.array, // Used to prevent cyclical Rule depedencies, or similar.
  chromeless: React.PropTypes.bool // Used to hide edit/delete buttons
};


function UnwrappedResourceForm({router, data, baseResource, children}) {

  let submit = function(e) {
    e.preventDefault();
    let headers = new Headers();
    headers.append('Content-Type', 'application/json');

    let params = { method: 'PUT',
                   headers: headers,
                   mode: 'cors',
                   body: JSON.stringify(data)
                 };

    let add = baseResource;

    if(data.id == "new") {
      add = baseResource.split("/new")[0];
      params.method = 'POST';
    }

    let post = new Request('http://localhost:5000/' + add);

    fetch(post,params).then(function(response) {
      if(response.ok) {
        router.goBack();
        //router.push('/' + baseResource.split("/")[0]);
      } else {
        console.log(response);
      }
    })

  }

  return (
    <form onSubmit={submit}>
      {children}
      <Button type="submit">
        Submit
      </Button>
    </form>
  )

}

UnwrappedResourceForm.propTypes = {
  data: React.PropTypes.shape({
    id: React.PropTypes.oneOfType([React.PropTypes.number, React.PropTypes.string]).isRequired
  }).isRequired,
  baseResource: React.PropTypes.string.isRequired
}

let ResourceForm = withRouter(UnwrappedResourceForm);
export { ResourceForm };


