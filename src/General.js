import React, { Component } from 'react';
import { LinkContainer } from 'react-router-bootstrap';
import { Button, Table, ControlLabel, FormControl, FormGroup, HelpBlock } from 'react-bootstrap';
import { withRouter } from 'react-router';

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

  render() {
    if (this.state) {
      const childrenWithProps = React.Children.map(this.props.children,
        (child) => React.cloneElement(child, {
          data: this.state.data,
          baseResource: this.props.baseResource,
          onServerDataChanged: this.onServerDataChanged.bind(this)
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

export function List({ columnNames, columns, baseResource, data, onServerDataChanged, onSelectHandler }) {

  // Stringify JSON objects(like check_metadata or other metadata objects in a row)
  for(let row of data) {
    for (let col of columns) {
      if(typeof row[col] === 'object') {
        row[col] = JSON.stringify(row[col]);
      }
    }
  }

  let deleteRow = (id) => {
    let headers = new Headers();
    headers.append('Content-Type', 'application/json');

    let params = { method: 'DELETE',
                   headers: headers,
                   mode: 'cors'
                 };

    let del = new Request('http://localhost:5000/' + baseResource + '/' + id);

    fetch(del, params).then(function(response) {
      onServerDataChanged();
    })
  }


  let selectEl = null;
  if(onSelectHandler) {    
    selectEl = (row) => {
      return <SelectToggle row={row} onSelectHandler={onSelectHandler} />
    };
  } else {
    selectEl = (row) => {};
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
                <Button onClick={deleteRow.bind(null, row.id)}>Delete</Button>
                {selectEl(row)}
              </td>
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
  onServerDataChanged: React.PropTypes.func.isRequired,
  onSelectHandler: React.PropTypes.func // If you want checkbox to display in list for selection, need a callback.
};

class SelectToggle extends Component {
  constructor(props) {
    super(props);
    this.state = { selected: false };
  }


  internalSelectHandler() {
    this.setState({selected: !this.state.selected});
    this.props.onSelectHandler(this.props.row);
  }

  render() {
    let text = this.state.selected ? "De-Select" : "Select"
    return <Button onClick={this.internalSelectHandler.bind(this)}>{text}</Button> 
  }

}

SelectToggle.propTypes = {
  row: React.PropTypes.object.isRequired,
  onSelectHandler: React.PropTypes.func.isRequired
}


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


