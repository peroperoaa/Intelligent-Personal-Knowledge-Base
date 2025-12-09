"use client";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { useContext, useState, useEffect } from "react";
import { AuthContext } from "./contexts/AuthContext";
import { FileUpload } from "@/components/ui/file-upload";
import axios from "axios";
import { toast } from "sonner";
import { motion } from "framer-motion";

export default function Page() {
  const { isLoggedIn } = useContext(AuthContext);
  const destination = isLoggedIn ? "/notespage" : "/login";
  const destination2 = isLoggedIn ? "/browse_pdfs" : "/login";

  // Intro State
  const [showIntro, setShowIntro] = useState(true);
  const [progress, setProgress] = useState(0);
  const [showEnter, setShowEnter] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(timer);
          setShowEnter(true);
          return 100;
        }
        // Randomize increment for more realistic feel
        const increment = Math.random() * 5 + 1; 
        return Math.min(prev + increment, 100);
      });
    }, 50);

    return () => clearInterval(timer);
  }, []);

  const handleEnter = () => {
    setShowIntro(false);
  };

  const handleUpload = async (data:FormData) => {
    try {
      const token = localStorage.getItem("accessToken");
      const response = await axios.post(`http://127.0.0.1:8000/add_pdf/`, data, {
        headers: {
          "Content-Type": "multipart/form-data",
          "Authorization": `Bearer ${token}`,
        },
        withCredentials: true
      });
      if (response.status === 201) {
        toast.success("File uploaded successfully");
      }
    } catch (error) {
      toast.error("Error uploading file");
    }
  }

  if (showIntro) {
     return (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-end pb-[190px] bg-black text-white overflow-hidden font-sans">
            {/* Background */}
            <div className="absolute inset-0 z-0">
                <video 
                    autoPlay 
                    loop 
                    muted 
                    playsInline
                    className={`w-full h-full object-cover transition-transform duration-[20s] ease-linear ${showEnter ? 'scale-110' : 'scale-100'}`}
                >
                    <source src="/images/kv-video.mp4" type="video/mp4" />
                </video>
                <div className="absolute inset-0 bg-black/30" />
            </div>

            {/* Content */}
            <div className="z-10 flex flex-col items-center w-full max-w-2xl px-4">
                {!showEnter ? (
                    <div className="w-full flex flex-col items-center space-y-6">
                        <Image
                            src="/images/jcczz.png"
                            alt="金铲铲之战"
                            width={500}
                            height={150}
                            className="drop-shadow-lg"
                        />
                        <div className="w-full max-w-md h-2 bg-gray-800/80 rounded-full overflow-hidden border border-blue-600/30 backdrop-blur-sm">
                            <motion.div 
                                className="h-full bg-gradient-to-r from-blue-600 via-blue-400 to-blue-200"
                                initial={{ width: "0%" }}
                                animate={{ width: `${progress}%` }}
                            />
                        </div>
                        <p className="text-blue-100/80 font-mono text-sm tracking-widest">
                            LOADING RESOURCES... {Math.floor(progress)}%
                        </p>
                    </div>
                ) : (
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                        className="flex flex-col items-center"
                    >
                        <Image 
                            src="/images/aag.png" 
                            alt="铲铲宝典" 
                            width={400} 
                            height={133}
                            className="mb-4 drop-shadow-[0_5px_5px_rgba(0,0,0,0.8)] cursor-pointer hover:scale-105 transition-transform duration-300"
                            onClick={handleEnter}
                        />
                    </motion.div>
                )}
            </div>
        </div>
     )
  }

  return (
      <div className="flex min-h-screen flex-col">
        <main className="flex-1">
          <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48">
            <div className="container px-4 md:px-6">
              <div className="grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_600px]">
                <div className="flex flex-col justify-center space-y-4">
                  <div className="space-y-2">
                    <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none">
                      Master the Arena with Golden Spatula Knowledge Base
                    </h1>
                    <p className="max-w-[600px] text-muted-foreground md:text-xl">
                      NoteCraft uses advanced AI to generate comprehensive, strategic guides from any TFT content. 
                      Climb the ladder, master compositions, and dominate the lobby.
                    </p>
                  </div>
                  <div className="flex flex-col gap-2 min-[400px]:flex-row">
                    <Button size="lg" asChild>
                      <Link href={destination}>Build your notes</Link>
                    </Button>
                    <Button variant="outline" size="lg" asChild>
                      <Link href={destination2}>Check out existing notes</Link>
                    </Button>
                  </div>
                </div>
                <div className="mx-auto flex items-center justify-center rounded-xl border bg-muted p-8">
                  <div className="space-y-4 bg-background rounded-lg p-6 shadow-sm w-full">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-red-500" />
                      <div className="h-3 w-3 rounded-full bg-yellow-500" />
                      <div className="h-3 w-3 rounded-full bg-green-500" />
                      <div className="ml-auto text-xs text-muted-foreground">Notecraft AI</div>
                    </div>
                    <div className="space-y-3">
                      <h3 className="font-semibold">Introduction to Machine Learning</h3>
                      <ul className="space-y-2 text-sm">
                        <li className="flex items-start gap-2">
                          <div className="rounded-full bg-primary/10 p-1">
                            <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                          </div>
                          <span>Machine Learning is a subset of artificial intelligence</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <div className="rounded-full bg-primary/10 p-1">
                            <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                          </div>
                          <span>Key concepts: supervised, unsupervised, and reinforcement learning</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <div className="rounded-full bg-primary/10 p-1">
                            <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                          </div>
                          <span>Applications include image recognition, natural language processing</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
              {isLoggedIn && <FileUpload 
                onChange={(files) => console.log('Files changed:', files)} 
                onSubmit={handleUpload} 
              />}
            </div>
          </section>
        </main>
      </div>
  );
}