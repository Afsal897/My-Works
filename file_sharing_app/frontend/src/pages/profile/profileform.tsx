import React,{useEffect} from "react";
import { Form, Row, Col, Button } from "react-bootstrap";
import { useForm } from "react-hook-form";
import { fetchProfileData, updateProfile } from "../../components/profile";
import { useNavbarContext } from "../home/navbarContext";
import { formatDateForInput } from "./profilehelpers";

interface Props {
  editMode: boolean;
  setError: (msg: string | null) => void;
  setSuccess: (msg: string | null) => void;
  setEditMode: (val: boolean) => void;
}

const ProfileForm: React.FC<Props> = ({
  editMode,
  setError,
  setSuccess,
  setEditMode,
}) => {
  const {
    firstName,
    lastName,
    username,
    email,
    dob,
    setFirstName,
    setLastName,
    setUsername,
    setEmail,
    setDOB,
  } = useNavbarContext();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    defaultValues: {
      first_name: "",
      last_name: "",
      username: "",
      email: "",
      dob: "",
    },
  });

  useEffect(() => {
      reset({
        first_name: firstName,
        last_name: lastName,
        username: username,
        email: email,
        dob: dob ? formatDateForInput(dob) : "",
      });
}, [reset, firstName, lastName, username, email, dob]);

  const onSubmit = async (data: any) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
      setError("Invalid email format.");
      return;
    }
    if(data.first_name.trim()===""){
      setError("First name cannot be empty")
      return
    }
    if(data.last_name.trim()===""){
      setError("Last name cannot be empty")
      return
    }
    if(data.email.trim()===""){
      setError("Email cannot be empty")
      return
    }
    try {
      const res = await updateProfile(data);
      if (res.status === 200) {
        const res= await fetchProfileData()
        const { first_name, last_name, username, email, dob } = res;
        setFirstName(first_name);
        setLastName(last_name);
        setUsername(username);
        setEmail(email);
        setDOB(dob);
        setError(null);
        setSuccess("Profile updated successfully.");
        setTimeout(() => {
          setSuccess(null);
        }, 1000);
        setEditMode(false);
        console.log("Profile updated successfully:", res);
      } else {
        setError(res.data.error);
      }
    } catch {
      setError("Failed to update profile.");
    }
  };

  return (
    <Form onSubmit={handleSubmit(onSubmit)}>
      <Row className="mb-3">
        <Col md={6}>
          <Form.Label>First Name</Form.Label>
          <Form.Control
            {...register("first_name")}
            readOnly={!editMode}
            isInvalid={!!errors.first_name}
          />
        </Col>
        <Col md={6}>
          <Form.Label>Last Name</Form.Label>
          <Form.Control
            {...register("last_name")}
            readOnly={!editMode}
            isInvalid={!!errors.last_name}
          />
        </Col>
      </Row>
      <Row className="mb-3">
        <Col md={6}>
          <Form.Label>Email</Form.Label>
          <Form.Control
            {...register("email")}
            readOnly={!editMode}
            isInvalid={!!errors.email}
          />
        </Col>
      </Row>
      <Row>
        <Col md={6}>
          <Form.Label>Date of Birth</Form.Label>
          <Form.Control {...register("dob")} readOnly={!editMode} />
        </Col>
      </Row>
      {editMode && (
        <div className="text-end mt-3">
          <Button type="submit" variant="success">
            Save Changes
          </Button>
        </div>
      )}
    </Form>
  );
};

export default ProfileForm;
