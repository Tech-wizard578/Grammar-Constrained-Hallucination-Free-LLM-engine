import { useState } from "react";
import { Button } from "./ui/button";
import { ingestDocuments, clearKnowledgeBase } from "@/lib/api";
import { 
  Plus, 
  Trash2, 
  Link2, 
  X, 
  Loader2, 
  CheckCircle, 
  AlertCircle,
  Upload
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogDescription,
} from "./ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "./ui/alert-dialog";
import { useToast } from "@/hooks/use-toast";

export function DocumentManager() {
  const [urls, setUrls] = useState<string[]>([""]);
  const [isIngesting, setIsIngesting] = useState(false);
  const [isClearing, setIsClearing] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);
  const { toast } = useToast();

  const addUrl = () => {
    setUrls([...urls, ""]);
  };

  const removeUrl = (index: number) => {
    setUrls(urls.filter((_, i) => i !== index));
  };

  const updateUrl = (index: number, value: string) => {
    const newUrls = [...urls];
    newUrls[index] = value;
    setUrls(newUrls);
  };

  const handleIngest = async () => {
    const validUrls = urls.filter((url) => url.trim());
    if (validUrls.length === 0) {
      toast({
        title: "No URLs provided",
        description: "Please enter at least one URL to ingest",
        variant: "destructive",
      });
      return;
    }

    setIsIngesting(true);
    setResult(null);

    try {
      const response = await ingestDocuments(validUrls);
      setResult({
        success: response.success,
        message: response.message || `Successfully indexed ${response.chunks_indexed} chunks`,
      });
      if (response.success) {
        setUrls([""]);
        toast({
          title: "Documents ingested",
          description: `Successfully indexed ${response.chunks_indexed} chunks`,
        });
      }
    } catch (error) {
      setResult({
        success: false,
        message: error instanceof Error ? error.message : "Ingestion failed",
      });
      toast({
        title: "Ingestion failed",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setIsIngesting(false);
    }
  };

  const handleClear = async () => {
    setIsClearing(true);
    try {
      const response = await clearKnowledgeBase();
      toast({
        title: response.success ? "Knowledge base cleared" : "Clear failed",
        description: response.message,
        variant: response.success ? "default" : "destructive",
      });
    } catch (error) {
      toast({
        title: "Clear failed",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setIsClearing(false);
    }
  };

  return (
    <div className="flex gap-2">
      <Dialog>
        <DialogTrigger asChild>
          <Button variant="outline" className="gap-2">
            <Upload className="w-4 h-4" />
            <span className="hidden sm:inline">Ingest Documents</span>
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-lg glass-card border-border">
          <DialogHeader>
            <DialogTitle className="gradient-text">Ingest Documents</DialogTitle>
            <DialogDescription>
              Add URLs to documents you want to index in the knowledge base.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 mt-4">
            <div className="space-y-3 max-h-[300px] overflow-y-auto scrollbar-thin">
              {urls.map((url, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-muted flex items-center justify-center">
                    <Link2 className="w-4 h-4 text-muted-foreground" />
                  </div>
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => updateUrl(index, e.target.value)}
                    placeholder="https://example.com/document"
                    className="flex-1 h-10 px-3 bg-muted/50 border border-border rounded-lg text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50"
                  />
                  {urls.length > 1 && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeUrl(index)}
                      className="flex-shrink-0"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={addUrl}
              className="w-full border border-dashed border-border"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Another URL
            </Button>

            {result && (
              <div
                className={`flex items-center gap-2 p-3 rounded-lg ${
                  result.success
                    ? "bg-success/10 text-success"
                    : "bg-destructive/10 text-destructive"
                }`}
              >
                {result.success ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  <AlertCircle className="w-4 h-4" />
                )}
                <span className="text-sm">{result.message}</span>
              </div>
            )}

            <Button
              variant="gradient"
              className="w-full"
              onClick={handleIngest}
              disabled={isIngesting}
            >
              {isIngesting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Ingesting...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Ingest Documents
                </>
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <AlertDialog>
        <AlertDialogTrigger asChild>
          <Button variant="outline" size="icon" className="text-destructive hover:text-destructive">
            <Trash2 className="w-4 h-4" />
          </Button>
        </AlertDialogTrigger>
        <AlertDialogContent className="glass-card border-border">
          <AlertDialogHeader>
            <AlertDialogTitle>Clear Knowledge Base?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete all documents from the knowledge base. 
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleClear}
              disabled={isClearing}
              className="bg-destructive hover:bg-destructive/90"
            >
              {isClearing ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <Trash2 className="w-4 h-4 mr-2" />
              )}
              Clear All
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
