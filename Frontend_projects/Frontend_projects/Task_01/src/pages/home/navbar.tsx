import React, { useEffect, useState } from "react";
import { Dropdown, Form, Navbar, Container, Nav } from "react-bootstrap";
import logo from '../../assets/logo.png'

interface MyNavbarProps {
  search: string;
  setSearch: (value: string) => void;
}

const MyNavbar: React.FC<MyNavbarProps> = ({ search, setSearch }) => {
  const [debouncedSearch, setDebouncedSearch] = useState(search);

  // Update debouncedSearch only after 500ms of no typing
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
    }, 500);

    return () => {
      clearTimeout(handler);
    };
  }, [search]);

  // Perform actions with debounced search value
  useEffect(() => {
    if (debouncedSearch) {
      console.log("Search value (debounced):", debouncedSearch);
      // e.g., API call
    }
  }, [debouncedSearch]);

  return (
    <Navbar bg="dark" variant="dark" expand="lg" className="px-3">
      <Container fluid>
        {/* Logo */}
         <Navbar.Brand href="/" className="d-flex align-items-center gap-2">
            <img
              src={logo}
              alt="App Logo"
              height="40"
              className="d-inline-block align-top"
            />
            <span className="fs-4 fw-semibold text-white">MyApp</span>
          </Navbar.Brand>

        {/* Search Bar */}
        <Form className="d-flex ms-auto me-3" style={{ maxWidth: 400, flexGrow: 1 }}>
          <Form.Control
            type="search"
            placeholder="Search"
            aria-label="Search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="me-2"
          />
        </Form>

        {/* Profile Dropdown */}
        <Nav>
          <Dropdown align="end">
            <Dropdown.Toggle variant="info" id="dropdown-profile">
              Profile
            </Dropdown.Toggle>

            <Dropdown.Menu>
              <Dropdown.Item href="/profile">Profile</Dropdown.Item>
              <Dropdown.Item href="/home/add_product">Add Product</Dropdown.Item>
              <Dropdown.Divider />
              <Dropdown.Item href="/logout">Logout</Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        </Nav>
      </Container>
    </Navbar>
  );
};

export default MyNavbar;
