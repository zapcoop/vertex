import React from 'react';
import uid from 'node-uuid';
import faker from 'faker';
import _ from 'underscore';
import moment from 'moment';
import { Link } from 'react-router';
import { LinkContainer } from 'react-router-bootstrap';

import {
  NavDropdown,
  Label,
  ListGroup,
  ListGroupItem,
  Media,
  Button,
  Navbar,
} from 'components';

const notifications = [
  {
    id: uid.v4(),
    icon: (
      <span className="fa-stack fa-lg">
        <i className="fa fa-circle-thin fa-stack-2x text-danger" />
        <i className="fa fa-close fa-stack-1x fa-fw text-danger" />
      </span>
    ),
    title: faker.hacker.phrase(),
    date: moment(faker.date.recent()).format('DD-MMM-YYYY, HH:mm'),
  },
  {
    id: uid.v4(),
    icon: (
      <span className="fa-stack fa-lg">
        <i className="fa fa-circle-thin fa-stack-2x text-primary" />
        <i className="fa fa-info fa-stack-1x text-primary" />
      </span>
    ),
    title: faker.hacker.phrase(),
    date: moment(faker.date.recent()).format('DD-MMM-YYYY, HH:mm'),
  },
  {
    id: uid.v4(),
    icon: (
      <span className="fa-stack fa-lg">
        <i className="fa fa-circle-thin fa-stack-2x text-success" />
        <i className="fa fa-check fa-stack-1x text-success" />
      </span>
    ),
    title: faker.hacker.phrase(),
    date: moment(faker.date.recent()).format('DD-MMM-YYYY, HH:mm'),
  },
  {
    id: uid.v4(),
    icon: (
      <span className="fa-stack fa-lg">
        <i className="fa fa-circle-thin fa-stack-2x text-warning" />
        <i className="fa fa-exclamation fa-stack-1x fa-fw text-warning" />
      </span>
    ),
    title: faker.hacker.phrase(),
    date: moment(faker.date.recent()).format('DD-MMM-YYYY, HH:mm'),
  },
];

class NotificationsDropdown extends React.Component {
  constructor() {
    super();

    this.state = {
      open: false,
    };
  }

  render() {
    return (
      <NavDropdown
        id="navbar-notifications"
        noCaret
        open={this.state.open}
        onToggle={() => {
          this.setState({ open: !this.state.open });
        }}
        title={
          <span>
            <span className="hidden-xs">
              <i className="fa fa-lg fa-fw fa-bell" />
              <Label bsStyle="primary" withIcon pill>
                10
              </Label>
            </span>

            <span className="hidden-sm hidden-md hidden-lg">
              Notifications
              <Label bsStyle="primary" className="m-l-1" pill>
                10
              </Label>
            </span>
          </span>
        }
      >
        <Navbar.DropdownList
          header={
            <div>
              <strong className="small text-uppercase">Notifications</strong>
              <Link to="/apps/user-profile/edit/settings">
                <Button
                  bsSize="xs"
                  onClick={() => {
                    this.setState({ open: false });
                  }}
                >
                  <i className="fa fa-gear fa-fw" />
                </Button>
              </Link>
            </div>
          }
          footer={
            <div
              className="text-center"
              onClick={() => this.setState({ open: false })}
            >
              See All Notifications <i className="fa fa-angle-right fa-fw" />
            </div>
          }
          footerUrl="/pages/timeline"
        >
          <ListGroup>
            {_.map(notifications, notification => (
              <ListGroupItem key={notification.id} href="javascript:;">
                <LinkContainer
                  to="/pages/timeline"
                  onClick={() => this.setState({ open: false })}
                >
                  <Media>
                    <Media.Left>{notification.icon}</Media.Left>
                    <Media.Body>
                      <p className="text-white">{notification.title}</p>
                      <p className="m-y-0 small">{notification.date}</p>
                    </Media.Body>
                  </Media>
                </LinkContainer>
              </ListGroupItem>
            ))}
          </ListGroup>
        </Navbar.DropdownList>
      </NavDropdown>
    );
  }
}

export default NotificationsDropdown;
