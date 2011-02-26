{-# LANGUAGE DeriveDataTypeable, ViewPatterns #-}
{-# OPTIONS_GHC -O2 -Wall #-}

import Prelude hiding (catch)
import Control.Applicative
import Control.Monad
import Control.Monad.CatchIO
import qualified Data.ByteString.Lazy as B
import Data.Char
import Data.Dynamic
import Data.Int
import qualified Data.Map as M
import Data.Time.Clock.POSIX
import Data.Time.Format
import Network.CGI
import Numeric
import System.FilePath
import System.IO
import System.IO.Error (isDoesNotExistError, isPermissionError)
import System.IO.Unsafe
import System.Locale
import System.Posix
import System.Posix.Handle

encodings :: M.Map String String
encodings = M.fromList [
             (".bz2", "bzip2"),
             (".gz", "gzip"),
             (".z", "compress")
            ]

types :: M.Map String String
types = M.fromList [
         (".avi", "video/x-msvideo"),
         (".css", "text/css"),
         (".doc", "application/msword"),
         (".gif", "image/gif"),
         (".htm", "text/html"),
         (".html", "text/html"),
         (".ico", "image/vnd.microsoft.icon"),
         (".il", "application/octet-stream"),
         (".jar", "application/java-archive"),
         (".jpeg", "image/jpeg"),
         (".jpg", "image/jpeg"),
         (".js", "application/x-javascript"),
         (".mid", "audio/midi"),
         (".midi", "audio/midi"),
         (".mov", "video/quicktime"),
         (".mp3", "audio/mpeg"),
         (".mpeg", "video/mpeg"),
         (".mpg", "video/mpeg"),
         (".otf", "application/octet-stream"),
         (".pdf", "application/pdf"),
         (".png", "image/png"),
         (".ppt", "application/vnd.ms-powerpoint"),
         (".ps", "application/postscript"),
         (".svg", "image/svg+xml"),
         (".swf", "application/x-shockwave-flash"),
         (".tar", "application/x-tar"),
         (".tgz", "application/x-gzip"),
         (".tif", "image/tiff"),
         (".tiff", "image/tiff"),
         (".ttf", "application/octet-stream"),
         (".wav", "audio/x-wav"),
         (".wmv", "video/x-ms-wmv"),
         (".xaml", "application/xaml+xml"),
         (".xap", "application/x-silverlight-app"),
         (".xhtml", "application/xhtml+xml"),
         (".xls", "application/vnd.ms-excel"),
         (".xml", "text/xml"),
         (".xsl", "text/xml"),
         (".zip", "application/zip")
        ]

data MyError = NotModified | Forbidden | NotFound | BadMethod | BadRange
    deriving (Show, Typeable)

instance Exception MyError

outputMyError :: MyError -> CGI CGIResult
outputMyError NotModified = setStatus 304 "Not Modified" >> outputNothing
outputMyError Forbidden = outputError 403 "Forbidden" []
outputMyError NotFound = outputError 404 "Not Found" []
outputMyError BadMethod = outputError 405 "Method Not Allowed" []
outputMyError BadRange = outputError 416 "Requested Range Not Satisfiable" []

checkExtension :: FilePath -> CGI ()
checkExtension file = do
  let (base, ext) = splitExtension file
  ext' <- case M.lookup (map toLower ext) encodings of
            Nothing -> return ext
            Just e -> do
              setHeader "Content-Encoding" e
              return $ takeExtension base

  case M.lookup (map toLower ext') types of
    Nothing -> throw Forbidden
    Just t -> setHeader "Content-Type" t

checkMethod :: CGI CGIResult -> CGI CGIResult
checkMethod rOutput = do
  m <- requestMethod
  case m of
    "HEAD" -> rOutput >> outputNothing
    "GET" -> rOutput
    "POST" -> rOutput
    _ -> throw BadMethod

httpDate :: String
httpDate = "%a, %d %b %Y %H:%M:%S %Z"
formatHTTPDate :: EpochTime -> String
formatHTTPDate = formatTime defaultTimeLocale httpDate .
                 posixSecondsToUTCTime . realToFrac
parseHTTPDate :: String -> Maybe EpochTime
parseHTTPDate = (fromInteger . floor . utcTimeToPOSIXSeconds <$>) .
                parseTime defaultTimeLocale httpDate

checkModified :: EpochTime -> CGI ()
checkModified mTime = do
  setHeader "Last-Modified" $ formatHTTPDate mTime
  (requestHeader "If-Modified-Since" >>=) $ maybe (return ()) $ \ims ->
      when (parseHTTPDate ims >= Just mTime) $ throw NotModified

checkIfRange :: EpochTime -> CGI (Maybe ())
checkIfRange mTime = do
  (requestHeader "If-Range" >>=) $ maybe (return $ Just ()) $ \ir ->
      return $ if parseHTTPDate ir == Just mTime then Just () else Nothing

parseRange :: String -> FileOffset -> Maybe (FileOffset, FileOffset)
parseRange (splitAt 6 -> ("bytes=", '-':(readDec -> [(len, "")]))) size =
    Just (max 0 (size - len), size - 1)
parseRange (splitAt 6 -> ("bytes=", readDec -> [(a, "-")])) size =
    Just (a, size - 1)
parseRange (splitAt 6 -> ("bytes=", readDec -> [(a, '-':(readDec -> [(b, "")]))])) size =
    Just (a, min (size - 1) b)
parseRange _ _ = Nothing

checkRange :: EpochTime -> FileOffset -> CGI (Maybe (FileOffset, FileOffset))
checkRange mTime size = do
  setHeader "Accept-Ranges" "bytes"
  (requestHeader "Range" >>=) $ maybe (return Nothing) $ \range -> do
  (checkIfRange mTime >>=) $ maybe (return Nothing) $ \() -> do
    case parseRange range size of
      Just (a, b) | a <= b -> return $ Just (a, b)
      Just _ -> throw BadRange
      Nothing -> return Nothing

outputAll :: Handle -> FileOffset -> CGI CGIResult
outputAll h size = do
  setHeader "Content-Length" $ show size
  outputFPS =<< liftIO (B.hGetContents h)

-- | Lazily read a given number of bytes from the handle into a
-- 'ByteString', then close the handle.
hGetClose :: Handle -> Int64 -> IO B.ByteString
hGetClose h len = do
  contents <- B.hGetContents h
  end <- unsafeInterleaveIO (hClose h >> return B.empty)
  return (B.append (B.take len contents) end)

outputRange :: Handle -> FileOffset -> Maybe (FileOffset, FileOffset) -> CGI CGIResult
outputRange h size Nothing = outputAll h size
outputRange h size (Just (a, b)) = do
  let len = b - a + 1

  setStatus 206 "Partial Content"
  setHeader "Content-Range" $
   "bytes " ++ show a ++ "-" ++ show b ++ "/" ++ show size
  setHeader "Content-Length" $ show len
  liftIO $ hSeek h AbsoluteSeek (fromIntegral a)
  outputFPS =<< liftIO (hGetClose h (fromIntegral len))

serveFile :: FilePath -> CGI CGIResult
serveFile file = (`catch` outputMyError) $ do
  checkExtension file

  checkMethod $ do

  let handleOpenError e =
          if isDoesNotExistError e then throw NotFound
          else if isPermissionError e then throw Forbidden
          else throw e
  h <- liftIO (openBinaryFile file ReadMode) `catch` handleOpenError
  (`onException` liftIO (hClose h)) $ do

  status <- liftIO $ hGetStatus h
  let mTime = modificationTime status
      size = fileSize status
  checkModified mTime

  range <- checkRange mTime size
  outputRange h size range

main :: IO ()
main = runCGI $ handleErrors $ serveFile =<< pathTranslated
