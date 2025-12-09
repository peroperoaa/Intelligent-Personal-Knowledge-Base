"use client";

import { useState, useContext } from "react";
import axios from "axios";
import SearchBar from "@/components/ui/searchbar";
import { toast } from "sonner";
import React from "react";
import "@/app/notespage/styles.css";
import { AuthContext } from "@/app/contexts/AuthContext";
import { Trash2 } from "lucide-react"; // Assuming lucide-react is available, or use text/emoji

interface Document {
  id: string;
  topic: string;
  uploaded_by: string;
  created_at: string;
  first_page_base64?: string;
  pdf_url: string;
}

const DocumentsPage = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const { username } = useContext(AuthContext);

  // Debugging logs
  console.log("Current logged in username:", username);

  const fetchDocuments = async (query: string) => {
    if (!query.trim()) return;
    
    setLoading(true);

    try {
      const response = await axios.get<{ result: Document[] }>(
        `http://127.0.0.1:8000/search_pdfs/?topic=${query}`
      );
      
      if (response.status === 204) {
        toast.error("No PDFs found.")
        setDocuments([]);
      } else {
        console.log(response.data.result);
        setDocuments(response.data.result);
      }
    } catch (err) {
      console.error("Error fetching documents:", err);
      toast.error("Failed to fetch documents.");
    }
    setLoading(false);
  };

  const handleDownload = async (e: React.MouseEvent, doc: Document) => {
    e.preventDefault();
    try {
      const response = await fetch(doc.pdf_url);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      let filename = doc.topic;
      if (!filename.toLowerCase().endsWith('.pdf')) {
        filename += '.pdf';
      }
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download failed:", err);
      window.open(doc.pdf_url, '_blank');
    }
  };

  const handleDelete = async (e: React.MouseEvent, docId: string) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this note?")) return;

    try {
      const accessToken = localStorage.getItem("accessToken");
      await axios.delete(`http://127.0.0.1:8000/delete_pdf/${docId}/`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      toast.success("Note deleted successfully");
      setDocuments(documents.filter((d) => d.id !== docId));
    } catch (err) {
      console.error("Error deleting document:", err);
      toast.error("Failed to delete note");
    }
  };

  return (
    <div className="min-h-screen p-6 p-6 flex flex-col items-center">
      <h1 className="text-3xl font-bold text-center mb-6">Search Strategies</h1>
      <p className="text-lg text-gray-600 mb-5 text-center max-w-xl">
        Enter a champion, trait, or composition to find relevant guides and notes.
      </p>
      <div className="flex flex-col items-center mb-6">
      <div className="max-w-md mb-2">
        <SearchBar onSearch={(query) => fetchDocuments(query)} />
      </div>
  
      <div className="h-6 flex items-center justify-center">
        {loading && <div className="loader"></div>}
      </div>
</div>

      

      {/* Document List */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {documents.map((doc) => {
           const isOwner = username === doc.uploaded_by;
           // console.log(`Doc: ${doc.topic}, UploadedBy: ${doc.uploaded_by}, CurrentUser: ${username}, IsOwner: ${isOwner}`);
           return (
          <div key={doc.id} className="relative group">
          <a
            href={doc.pdf_url}
            onClick={(e) => handleDownload(e, doc)}
            className="block bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition duration-300 cursor-pointer h-full"
          >
            {doc.first_page_base64 ? (
              <img
                src={`data:image/png;base64,${doc.first_page_base64}`}
                alt={doc.topic}
                className="w-full h-40 object-cover rounded-md"
              />
            ) : (
              <div className="w-full h-40 flex items-center justify-center bg-gray-200 rounded-md">
                No Preview Available
              </div>
            )}
            <h2 className="mt-2 text-lg font-semibold">{doc.topic}</h2>
            <p className="text-gray-500">By: {doc.uploaded_by}</p>
            <p className="text-gray-400 text-sm">
              Created: {new Date(doc.created_at).toLocaleDateString()}
            </p>
          </a>
          {isOwner && (
            <button
              onClick={(e) => handleDelete(e, doc.id)}
              className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600 z-20"
              title="Delete Note"
            >
              <Trash2 size={16} />
            </button>
          )}
          </div>
        )})}
      </div>
    </div>
  );
};

export default DocumentsPage;
