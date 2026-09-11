import "./globals.css";

export const metadata = {
  title: "UdyamSaathi",
  description: "A clearer path from your situation to a brighter tomorrow.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
