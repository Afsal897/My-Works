import React, { useState } from "react";
import MyNavbar from "./navbar";
import { Container, Form, Button, Card } from "react-bootstrap";
import {
  handleUploadSubmit,
  handleFileChange,
} from "../../components/home/addproduct";

const AddProduct: React.FC = () => {
  const [search, setSearch] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  return (
    <>
      <MyNavbar search={search} setSearch={setSearch} />

      <Container className="mt-5" style={{ maxWidth: 600 }}>
        <Card className="p-4 shadow rounded-4">
          <h3 className="mb-4 text-center">Add New Product</h3>
          <Form
            onSubmit={(e) =>
              handleUploadSubmit(
                e,
                file,
                description,
                setFile,
                setDescription,
                setError,
                setSuccess
              )
            }
          >
            <Form.Group className="mb-3">
              <Form.Label>
                Description<span className="text-danger">*</span>
              </Form.Label>
              <Form.Control
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Enter product description"
              />
            </Form.Group>

            <Form.Group className="mb-4">
              <Form.Label>
                Upload File<span className="text-danger">*</span>
                <p>(allowed file types are jpg, jpeg, png)</p>
              </Form.Label>
              <Form.Control
                type="file"
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  handleFileChange(e, setFile)
                }
                // accept=".jpg,.jpeg,.png"
              />
            </Form.Group>

            <Button variant="primary" type="submit" className="w-100">
              Upload Product
            </Button>
          </Form>
          {error && (
            <div className="alert alert-danger mt-3" role="alert">
              {error}
            </div>
          )}
          {success && (
            <div className="alert alert-success mt-3" role="alert">
              {success}
            </div>
          )}
        </Card>
      </Container>
    </>
  );
};

export default AddProduct;
