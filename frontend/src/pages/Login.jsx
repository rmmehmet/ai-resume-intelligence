import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Couldn't log in. Check your email and password.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="container" style={{ maxWidth: 400, paddingTop: 64 }}>
      <h1>Log in</h1>
      <p style={{ color: "var(--color-text-muted)" }}>
        Welcome back. Pick up where you left off.
      </p>

      <form onSubmit={handleSubmit} className="card" style={{ marginTop: 24 }}>
        <div className="field">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className="field">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {error && <p className="error-text">{error}</p>}

        <button type="submit" className="btn btn-primary" disabled={isSubmitting} style={{ width: "100%" }}>
          {isSubmitting ? "Logging in..." : "Log in"}
        </button>
      </form>

      <p style={{ marginTop: 16, fontSize: "0.9rem" }}>
        No account yet? <Link to="/register">Create one</Link>
      </p>
    </div>
  );
}