-- Seed sticker variant pricing matrix
-- Materials: vinyl, holographic, transparent, kraft_paper, paper
-- Pack quantities: 10, 25, 50, 100, 250

-- This table is reference-only; actual variant rows are generated per product.
-- We store the pricing matrix as a simple lookup table for the generation pipeline.

CREATE TABLE IF NOT EXISTS pricing_matrix (
  material TEXT NOT NULL,
  pack_quantity INT NOT NULL,
  retail_price NUMERIC(10,2) NOT NULL,
  PRIMARY KEY (material, pack_quantity)
);

INSERT INTO pricing_matrix (material, pack_quantity, retail_price) VALUES
('vinyl', 10, 4.99),
('vinyl', 25, 9.99),
('vinyl', 50, 16.99),
('vinyl', 100, 29.99),
('vinyl', 250, 64.99),
('holographic', 10, 7.99),
('holographic', 25, 15.99),
('holographic', 50, 26.99),
('holographic', 100, 47.99),
('holographic', 250, 104.99),
('transparent', 10, 5.99),
('transparent', 25, 11.99),
('transparent', 50, 19.99),
('transparent', 100, 34.99),
('transparent', 250, 74.99),
('kraft_paper', 10, 4.49),
('kraft_paper', 25, 8.99),
('kraft_paper', 50, 14.99),
('kraft_paper', 100, 26.99),
('kraft_paper', 250, 57.99),
('paper', 10, 3.99),
('paper', 25, 7.99),
('paper', 50, 12.99),
('paper', 100, 22.99),
('paper', 250, 49.99)
ON CONFLICT DO NOTHING;
