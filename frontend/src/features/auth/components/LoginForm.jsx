import { ArrowRight, Eye, EyeOff, Lock, Mail } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { TextField } from "../../../components/forms/TextField.jsx";
import { Button } from "../../../components/ui/Button.jsx";
import { useAuth } from "../authContext.js";

const initialValues = {
  email: "",
  password: "",
  remember: false,
};

function validate(values) {
  const errors = {};

  if (!values.email.trim()) {
    errors.email = "Email address is required.";
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email.trim())) {
    errors.email = "Enter a valid work email address.";
  }

  if (!values.password) {
    errors.password = "Password is required.";
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
      await login({
        email: values.email.trim(),
        password: values.password,
      });

      navigate("/dashboard", { replace: true });
    } catch (error) {
      if (error.response?.status === 401) {
        setFormMessage("The email or password is incorrect.");
      } else if (error.response?.status >= 500) {
        setFormMessage("Unable to connect to the server. Please try again.");
      } else {
        setFormMessage("Unable to connect to the server. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="login-form" onSubmit={handleSubmit} noValidate>
      <TextField
        autoComplete="email"
        error={errors.email}
        id="email"
        label="Email Address"
        leftSlot={<Mail aria-hidden="true" size={18} />}
        name="email"
        onChange={updateField}
        placeholder="Enter your email"
        type="email"
        value={values.email}
      />

      <TextField
        autoComplete="current-password"
        error={errors.password}
        id="password"
        label="Password"
        leftSlot={<Lock aria-hidden="true" size={18} />}
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
