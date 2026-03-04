import React, { useState, useRef } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { askQuestion } from "./api";

export default function HomeScreen() {
  const insets = useSafeAreaInsets();
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  const handleSend = async () => {
    const q = question.trim();
    if (!q || loading) return;

    // Add user message
    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setQuestion("");
    setLoading(true);

    try {
      const result = await askQuestion(q);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: result.answer,
          verses: result.verses,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "error", text: `Error: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 100);
    }
  };

  return (
    <KeyboardAvoidingView
      style={[styles.container, { paddingTop: insets.top }]}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      keyboardVerticalOffset={0}
    >
      <StatusBar style="light" />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>KJB-LLM</Text>
        <Text style={styles.headerSubtitle}>
          Ask anything — answered from the King James Bible
        </Text>
      </View>

      {/* Messages */}
      <ScrollView
        ref={scrollRef}
        style={styles.messages}
        contentContainerStyle={styles.messagesContent}
      >
        {messages.length === 0 && (
          <View style={styles.emptyState}>
            <Text style={styles.emptyIcon}>📖</Text>
            <Text style={styles.emptyText}>
              Ask a question in your own words and receive an answer grounded
              entirely in the King James Bible.
            </Text>
            <Text style={styles.emptyHint}>
              Try: "What does the Bible say about forgiveness?"
            </Text>
          </View>
        )}

        {messages.map((msg, idx) => (
          <View
            key={idx}
            style={[
              styles.bubble,
              msg.role === "user"
                ? styles.userBubble
                : msg.role === "error"
                ? styles.errorBubble
                : styles.assistantBubble,
            ]}
          >
            <Text
              style={[
                styles.bubbleText,
                msg.role === "user" && styles.userBubbleText,
              ]}
            >
              {msg.text}
            </Text>

            {/* Show supporting verses for assistant responses */}
            {msg.verses && msg.verses.length > 0 && (
              <View style={styles.versesContainer}>
                <Text style={styles.versesHeader}>Supporting verses:</Text>
                {msg.verses.slice(0, 5).map((v, vi) => (
                  <Text key={vi} style={styles.verseItem}>
                    <Text style={styles.verseRef}>{v.reference}</Text>
                    {"  "}
                    {v.text.length > 150
                      ? v.text.substring(0, 150) + "..."
                      : v.text}
                  </Text>
                ))}
              </View>
            )}
          </View>
        ))}

        {loading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="small" color="#c9a227" />
            <Text style={styles.loadingText}>Searching the scriptures...</Text>
          </View>
        )}
      </ScrollView>

      {/* Input */}
      <View style={[styles.inputRow, { paddingBottom: insets.bottom + 8 }]}>
        <TextInput
          style={styles.input}
          value={question}
          onChangeText={setQuestion}
          placeholder="Ask the King James Bible..."
          placeholderTextColor="#888"
          onSubmitEditing={handleSend}
          returnKeyType="send"
          editable={!loading}
          multiline
        />
        <TouchableOpacity
          style={[styles.sendBtn, (!question.trim() || loading) && styles.sendBtnDisabled]}
          onPress={handleSend}
          disabled={!question.trim() || loading}
        >
          <Text style={styles.sendBtnText}>Ask</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#1a1a2e",
  },
  header: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#2a2a4a",
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: "700",
    color: "#c9a227",
  },
  headerSubtitle: {
    fontSize: 13,
    color: "#aaa",
    marginTop: 2,
  },

  messages: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
    paddingBottom: 8,
  },

  emptyState: {
    alignItems: "center",
    marginTop: 60,
    paddingHorizontal: 32,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyText: {
    color: "#ccc",
    fontSize: 15,
    textAlign: "center",
    lineHeight: 22,
  },
  emptyHint: {
    color: "#888",
    fontSize: 13,
    textAlign: "center",
    marginTop: 16,
    fontStyle: "italic",
  },

  bubble: {
    borderRadius: 16,
    padding: 14,
    marginBottom: 10,
    maxWidth: "85%",
  },
  userBubble: {
    backgroundColor: "#c9a227",
    alignSelf: "flex-end",
    borderBottomRightRadius: 4,
  },
  assistantBubble: {
    backgroundColor: "#2a2a4a",
    alignSelf: "flex-start",
    borderBottomLeftRadius: 4,
  },
  errorBubble: {
    backgroundColor: "#4a1a1a",
    alignSelf: "flex-start",
    borderBottomLeftRadius: 4,
  },
  bubbleText: {
    color: "#eee",
    fontSize: 15,
    lineHeight: 22,
  },
  userBubbleText: {
    color: "#1a1a2e",
  },

  versesContainer: {
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: "#3a3a5a",
  },
  versesHeader: {
    color: "#c9a227",
    fontSize: 12,
    fontWeight: "600",
    marginBottom: 6,
  },
  verseItem: {
    color: "#bbb",
    fontSize: 12,
    lineHeight: 18,
    marginBottom: 4,
  },
  verseRef: {
    fontWeight: "700",
    color: "#c9a227",
  },

  loadingContainer: {
    flexDirection: "row",
    alignItems: "center",
    alignSelf: "flex-start",
    paddingVertical: 8,
  },
  loadingText: {
    color: "#aaa",
    fontSize: 13,
    marginLeft: 8,
    fontStyle: "italic",
  },

  inputRow: {
    flexDirection: "row",
    alignItems: "flex-end",
    paddingHorizontal: 12,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: "#2a2a4a",
    backgroundColor: "#1a1a2e",
  },
  input: {
    flex: 1,
    backgroundColor: "#2a2a4a",
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    color: "#eee",
    fontSize: 15,
    maxHeight: 100,
  },
  sendBtn: {
    backgroundColor: "#c9a227",
    borderRadius: 20,
    paddingHorizontal: 18,
    paddingVertical: 10,
    marginLeft: 8,
  },
  sendBtnDisabled: {
    opacity: 0.4,
  },
  sendBtnText: {
    color: "#1a1a2e",
    fontWeight: "700",
    fontSize: 15,
  },
});
