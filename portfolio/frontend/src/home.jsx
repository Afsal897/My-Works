import React, { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const ContactForm = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    message: "",
  });

  const [errors, setErrors] = useState({});
  const [submitted, setSubmitted] = useState(false);

  const validate = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = "Name is required";
    } else if (formData.name.length < 3) {
      newErrors.name = "Name must be at least 3 characters";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/^\S+@\S+\.\S+$/.test(formData.email)) {
      newErrors.email = "Email is not valid";
    }

    if (formData.phone && !/^\d{10,15}$/.test(formData.phone)) {
      newErrors.phone = "Phone must be 10–15 digits (optional)";
    }

    if (!formData.message.trim()) {
      newErrors.message = "Message is required";
    } else if (formData.message.length < 10) {
      newErrors.message = "Message must be at least 10 characters";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setErrors({ ...errors, [e.target.name]: "" }); // Clear error on change
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      const response = await fetch("http://localhost:5000/contact_form", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (response.ok) {
        setSubmitted(true);
        setFormData({ name: "", email: "", phone: "", message: "" });
        setErrors({});
        setTimeout(() => setSubmitted(false), 4000);
      }
    } catch (err) {
      console.error("Failed to send contact form:", err);
    }
  };

  return (
    <div className="p-4 bg-dark text-white py-5 rounded">
      <h5 className="mb-4 text-center">Contact Me</h5>
      <form onSubmit={handleSubmit} noValidate className="needs-validation">
        {/* Row for Name and Phone */}
        <div className="row mb-3">
          <div className="col-md-6 mb-3">
            <input
              type="text"
              name="name"
              placeholder="Your Name"
              value={formData.name}
              onChange={handleChange}
              className="form-control"
            />
            {errors.name && (
              <small className="text-danger">{errors.name}</small>
            )}
          </div>

          <div className="col-md-6">
            <input
              type="tel"
              name="phone"
              placeholder="Your Phone (optional)"
              value={formData.phone}
              onChange={handleChange}
              className="form-control"
            />
            {errors.phone && (
              <small className="text-danger">{errors.phone}</small>
            )}
          </div>
        </div>

        {/* Email */}
        <div className="mb-3 w-80">
          <input
            type="email"
            name="email"
            placeholder="Your Email"
            value={formData.email}
            onChange={handleChange}
            className="form-control"
          />
          {errors.email && (
            <small className="text-danger">{errors.email}</small>
          )}
        </div>

        {/* Message */}
        <div className="mb-3">
          <textarea
            name="message"
            rows={4}
            placeholder="Your Message"
            value={formData.message}
            onChange={handleChange}
            className="form-control"
          />
          {errors.message && (
            <small className="text-danger">{errors.message}</small>
          )}
        </div>

        {/* Submit */}
        <div className="text-center mt-4">
          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: "30%" }}
          >
            Send Message
          </button>
        </div>

        {submitted && (
          <p className="mt-3 text-success text-center">Message sent! ✅</p>
        )}
      </form>
    </div>
  );
};

const Home = () => {
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await axios.get("http://localhost:5000/projects");
      setProjects(res.data);
    } catch (err) {
      console.error("Error fetching projects", err);
    }
  };

  return (
    <div className="d-flex flex-column min-vh-100 bg-light text-dark">
      <nav className="navbar navbar-expand-lg navbar-dark bg-black fixed-top shadow py-4">
        <div className="container d-flex align-items-center justify-content-between">
          <h2 className="text-light fw-bold display-6 mb-0 ms-2 align-items-start">
            AFSAL SALIM
          </h2>
          <button
            className="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarNav"
            aria-controls="navbarNav"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          <div
            className="collapse navbar-collapse justify-content-end"
            id="navbarNav"
          >
            <ul className="navbar-nav">
              <li className="nav-item">
                <a className="nav-link text-light" href="#home">
                  Home
                </a>
              </li>
              <li className="nav-item">
                <a className="nav-link text-light" href="#projects">
                  Projects
                </a>
              </li>
              <li className="nav-item">
                <a className="nav-link text-light" href="#contact">
                  Contact
                </a>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section
        id="home"
        className="animated-bg bg-dark text-white d-flex align-items-center"
        style={{ minHeight: "100vh", paddingTop: "100px" }}
      >
        <div className="container">
          <div className="row align-items-center">
            {/* Left Column - Profile */}
            <div className="col-md-4 text-center mb-4 mb-md-0">
              <img
                src="/src/assets/my-photo.png"
                alt="Avatar"
                className="rounded-circle border border-white shadow mb-4 img-fluid"
                style={{
                  width: "220px",
                  height: "220px",
                  objectFit: "cover",
                  transition: "transform 0.3s ease-in-out",
                }}
                onMouseOver={(e) =>
                  (e.currentTarget.style.transform = "scale(1.05)")
                }
                onMouseOut={(e) =>
                  (e.currentTarget.style.transform = "scale(1)")
                }
              />
              <h2 className="fw-bold text-uppercase">AFSAL SALIM</h2>
              <p className="fw-bold text-uppercase">
                Fullstack Engineer | AI Enthusiast
              </p>
            </div>

            {/* Right Column - About */}
            <div className="col-md-8">
              <h1 className="fw-bold display-5 mb-4 border-bottom pb-2">
                About Me
              </h1>
              <p className="fs-5 lh-lg">
                I am a dedicated and results-driven full-stack engineer,
                currently working at <strong>Innovature</strong>, with extensive
                hands-on experience in building intelligent, scalable, and
                high-performance web applications. My backend expertise includes
                <strong> Flask</strong>, <strong>Django</strong>, and{" "}
                <strong>FastAPI</strong>, while on the frontend I use{" "}
                <strong>React</strong> and <strong>TypeScript</strong>. I'm
                passionate about AI, working on projects in <strong>ML</strong>,{" "}
                <strong>DL</strong>, <strong>Computer Vision</strong>,{" "}
                <strong>Generative AI</strong>, and <strong>LLMs</strong>.
              </p>
              <a href="#contact" className="btn btn-outline-light mt-3">
                Contact Me
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Projects Section */}
      <section
        id="projects"
        className=" py-5 projects-gradient-bg"
        style={{ backgroundColor: "#FFF1E6" }}
      >
        <div className="container">
          <h3 className="text-center fw-bold mb-4">Projects</h3>
          <div className="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
            {projects.map((project) => (
              <div className="col" key={project.id}>
                <div className="card h-100 shadow border-0">
                  <img
                    src={project.image_url}
                    className="card-img-top"
                    alt={project.title}
                    style={{ height: "200px", objectFit: "cover" }}
                  />
                  <div
                    className="card-body"
                    style={{ backgroundColor: "#F8EEEC" }}
                  >
                    <h5 className="card-title">{project.title}</h5>
                    <p className="card-text">{project.description}</p>

                    {project.skills?.length > 0 && (
                      <div className="mb-2">
                        <strong>Skills:</strong>
                        <div className="d-flex flex-wrap gap-2 mt-1">
                          {project.skills.map((skill, index) => (
                            <span
                              key={index}
                              className="badge bg-secondary text-white"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <a
                      href={project.live_demo_url || project.github_url}
                      target="_blank"
                      rel="noreferrer"
                      className="btn btn-outline-primary btn-sm mt-2"
                    >
                      View Project
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* footer Section */}
      <footer id="contact" className="projects-gradient-bg bg-dark text-white">
        <div className="container ">
          <div className="row justify-content-center align-items-center">
            {/* Left Side: Resume + Social + Email */}
            <div className="col-md-5 mb-5 mb-md-0 d-flex flex-column justify-content-center h-100">
              <div className="pe-md-4 text-center gap-5 d-flex flex-column">
                {/* Resume */}
                <div className="mb-4 text-center">
                  <img
                    src="/src/assets/resume.png"
                    alt="Resume Icon"
                    width="40"
                    height="40"
                    className="mb-2"
                  />
                  <h5 className="mb-3">Resume</h5>
                  <a
                    href="/src/assets/afsal.pdf"
                    download
                    className="btn btn-outline-light"
                  >
                    Download Resume
                  </a>
                </div>

                {/* Social Icons */}
                <div className="pt-2 small">
                  <div className="d-flex flex-column align-items-center justify-content-center mb-2 text-center">
                    {/* Social Icons */}
                    <div className="d-flex gap-3 mb-2">
                      <a
                        href="https://www.linkedin.com/in/afsal-salim-97b880288/"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <img
                          src="/src/assets/linkedin.png"
                          alt="LinkedIn"
                          width="32"
                          height="32"
                        />
                      </a>
                      <a
                        href="https://github.com/Afsal897"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <img
                          src="/src/assets/github.png"
                          alt="GitHub"
                          width="32"
                          height="32"
                        />
                      </a>
                    </div>

                    {/* Email */}
                    <p className="mb-1 text-light fw-semibold">
                      📧 afsalsalim897@gmail.com
                    </p>
                    <p className="mb-0 text-light fw-semibold">
                      📍 Kerala, India
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Divider */}
            <div className="d-none d-md-block col-md-1">
              <div
                style={{
                  borderLeft: "1px solid rgba(255, 255, 255, 0.2)",
                  height: "100%",
                  margin: "0 auto",
                }}
              ></div>
            </div>

            {/* Right Side: Contact Form */}
            <div className="col-md-6 mt-5 mt-md-0">
              <div className="bg-dark p-4 rounded">
                <ContactForm />
              </div>
            </div>
          </div>
        </div>
        <div className="pt-2 text-center border-top border-secondary mt-3">
          <p className="mb-0 text-light">&copy; 2025 Afsal Salim</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;
