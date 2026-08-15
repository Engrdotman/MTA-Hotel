import { ArrowRight, Eye, EyeOff, Mail } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { TextField } from "../../../components/forms/TextField.jsx";
import { Button } from "../../../components/ui/Button.jsx";
import { useAuth } from "../authContext.js";

const initialValues = {
  email: "",
  password: "",
  remember: false,
  role: "front_desk",
};

const roleOptions = [
  { label: "Front desk", value: "front_desk" },
  { label: "Manager", value: "manager" },
  { label: "Admin", value: "admin" },
];

function validate(values) {
  const errors = {};

  if (!values.email.trim()) {
    errors.email = "Email address is required.";
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email.trim())) {
    errors.email = "Enter a valid work email address.";
  }

  if (!values.password) {
    errors.password = "Password is required.";
  } else if (values.password.length < 8) {
    errors.password = "Password must be at least 8 characters.";
  }

  return errors;
}

export function LoginForm() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formMessage, setFormMessage] = useState("");

  function updateField(event) {
    const { checked, name, type, value } = event.target;
    setValues((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value,
    }));
    setErrors((current) => ({ ...current, [name]: "" }));
    setFormMessage("");
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const nextErrors = validate(values);
    setErrors(nextErrors);

    if (Object.keys(nextErrors).length > 0 || isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    setFormMessage("");

    try {
      // Map UI role selection to actual role names
      const roleMap = {
        front_desk: "RECEPTIONIST",
        manager: "MANAGER",
        admin: "ADMIN",
      };
      const selectedRole = roleMap[values.role];

      // Login and get user data
      const user = await login({
        email: values.email.trim(),
        password: values.password,
      });

      // Check if user has the selected role
      if (user.role !== selectedRole) {
        setFormMessage(`Access denied. You have "${user.role}" role, not "${values.role}". Please use appropriate credentials.`);
        setIsSubmitting(false);
        return;
      }

      navigate("/dashboard", { replace: true });
    } catch (error) {
      if (error.response?.status === 401) {
        setFormMessage("Invalid email or password.");
      } else if (error.response?.status >= 500) {
        setFormMessage("The server is unavailable right now. Please try again shortly.");
      } else {
        setFormMessage("Unable to sign in. Please check your connection and try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="login-form" onSubmit={handleSubmit} noValidate>
      <fieldset className="role-selector" aria-label="Account type">
        {roleOptions.map((option) => (
          <label key={option.value}>
            <input
              checked={values.role === option.value}
              name="role"
              onChange={updateField}
              type="radio"
              value={option.value}
            />
            <span>{option.label}</span>
          </label>
        ))}
      </fieldset>

      <TextField
        autoComplete="email"
        error={errors.email}
        id="email"
        label="Email Address"
        name="email"
        onChange={updateField}
        placeholder="Enter your email"
        rightSlot={<Mail aria-hidden="true" size={18} />}
        type="email"
        value={values.email}
      />

      <TextField
        autoComplete="current-password"
        error={errors.password}
        id="password"
        label="Password"
        name="password"
        onChange={updateField}
        placeholder="Enter your password"
        rightSlot={
          <button
            aria-label={isPasswordVisible ? "Hide password" : "Show password"}
            className="password-toggle"
            onClick={() => setIsPasswordVisible((current) => !current)}
            type="button"
          >
            {isPasswordVisible ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        }
        type={isPasswordVisible ? "text" : "password"}
        value={values.password}
      />

      <div className="form-options">
        <label className="checkbox-label">
          <input
            checked={values.remember}
            name="remember"
            onChange={updateField}
            type="checkbox"
          />
          <span>Remember me</span>
        </label>
        <a href="/login">Forgot password?</a>
      </div>

      {formMessage ? (
        <p className="form-message" role="status">
          {formMessage}
        </p>
      ) : null}

      <Button
        icon={<ArrowRight aria-hidden="true" size={18} />}
        isLoading={isSubmitting}
        type="submit"
      >
        Sign In
      </Button>
    </form>
  );
}
