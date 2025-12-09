"use client";
import React, { useState, useContext } from "react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { toast } from "sonner";
import { AuthContext } from "@/app/contexts/AuthContext";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const { setIsLoggedIn } = useContext(AuthContext);
  
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    confirmPassword: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const { username, password, confirmPassword } = formData;

    if (!username || !password) {
      toast.error("All fields are required.");
      return;
    }

    if (!isLogin && password !== confirmPassword) {
      toast.error("Passwords do not match.");
      return;
    }

    try {
      const endpoint = isLogin ? "login/" : "signup/";
      const payload = isLogin 
        ? { username, password }
        : { username, password, confirm_password: confirmPassword };

      const response = await axios.post(
        `http://127.0.0.1:8000/api/${endpoint}`,
        payload,
        {
          headers: { "Content-Type": "application/json" },
          withCredentials: true,
        }
      );

      if (isLogin) {
        if (response.status === 200) {
          const data = response.data;
          localStorage.setItem("accessToken", data.access);
          localStorage.setItem("refreshToken", data.refresh);
          localStorage.setItem("isLoggedIn", "true");
          setIsLoggedIn(true);
          toast.success("Logged in successfully");
          onSuccess();
        }
      } else {
        if (response.status === 201) {
          toast.success("Signed up successfully. Please login.");
          setIsLogin(true);
          setFormData({ username: "", password: "", confirmPassword: "" });
        }
      }
    } catch (error) {
      console.error(error);
      toast.error(isLogin ? "Login failed" : "Signup failed");
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="relative w-full max-w-md p-8 bg-black/80 border border-blue-500/30 rounded-2xl backdrop-blur-md"
          >
            {/* Close button */}
            <button 
                onClick={onClose}
                className="absolute top-4 right-4 text-gray-400 hover:text-white"
            >
                ✕
            </button>

            <h2 className="text-3xl font-bold text-center mb-8 text-transparent bg-clip-text bg-gradient-to-r from-blue-200 to-blue-500">
              {isLogin ? "Welcome Back" : "Join the Arena"}
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <input
                  type="text"
                  name="username"
                  placeholder="Username"
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-blue-500/50 text-white placeholder-gray-500 transition-colors"
                />
              </div>
              <div>
                <input
                  type="password"
                  name="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-blue-500/50 text-white placeholder-gray-500 transition-colors"
                />
              </div>
              {!isLogin && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                >
                  <input
                    type="password"
                    name="confirmPassword"
                    placeholder="Confirm Password"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-blue-500/50 text-white placeholder-gray-500 transition-colors"
                  />
                </motion.div>
              )}

              <button
                type="submit"
                className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-blue-400 hover:from-blue-500 hover:to-blue-300 text-white font-bold rounded-lg shadow-lg transform transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                {isLogin ? "Login" : "Sign Up"}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-gray-400 text-sm">
                {isLogin ? "Don't have an account? " : "Already have an account? "}
                <button
                  onClick={() => setIsLogin(!isLogin)}
                  className="text-blue-400 hover:text-blue-300 font-semibold underline decoration-transparent hover:decoration-blue-300 transition-all"
                >
                  {isLogin ? "Sign Up" : "Login"}
                </button>
              </p>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
